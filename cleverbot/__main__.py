from __future__ import absolute_import, print_function

import argparse
import getpass
import inspect
import os
import pickle
import sys
from distutils.version import StrictVersion

import cleverbot
from cleverbot.migrations import migratables
from cleverbot.utils import get_migrations


class KwargsParser(argparse.ArgumentParser):

    def _parse_optional(self, arg_string):
        option_tuple = super(KwargsParser, self)._parse_optional(arg_string)
        long_option = all(char in self.prefix_chars for char in arg_string[:2])
        if long_option and option_tuple == (None, arg_string, None):
            action, option_string, explicit_arg = option_tuple
            action = argparse._StoreAction(
                **self._get_optional_kwargs(arg_string))
            option_tuple = (action, option_string, explicit_arg)
        return option_tuple


class SubParsersAction(argparse._SubParsersAction):

    def __call__(self, parser, namespace, values, option_string=None):
        super(SubParsersAction, self).__call__(
            parser, namespace, values, option_string)
        parser_name = values[0]
        parser.func = globals()[parser_name]


def prompt(text, required=False, hidden=False):
    while True:
        if hidden:
            value = getpass.getpass(text)
        else:
            # input writes to stdout
            sys.stderr.write(text)
            sys.stderr.flush()
            if sys.version_info.major == 2:
                value = raw_input()
            else:
                value = input()
        if value or not required:
            return value


def core(parser, args):
    if not args.key:
        args.key = prompt("Your Cleverbot API key: ", required=True,
                          hidden=True)
    cb = cleverbot.Cleverbot(**vars(args))
    try:
        while True:
            text = prompt(">>> ")
            try:
                print(cb.say(text))
            except cleverbot.CleverbotError as error:
                parser.error(error)
    finally:
        cb.close()


def say(parser, args):
    cb = cleverbot.Cleverbot(vars(args).pop('key'))
    try:
        print(cb.say(**vars(args)))
    except cleverbot.CleverbotError as error:
        parser.error(error)
    finally:
        cb.close()


def migrate(parser, args):

    def get_version(object):
        if (isinstance(object, tuple) and len(object) == 2 and
                isinstance(object[0], dict) and isinstance(object[1], list)):
            keys = list(object[0])
            items = ['key', 'cs', 'timeout']
            tweaks = ['tweak1', 'tweak2', 'tweak3']
            if keys == items:
                return '2.1.1'
            elif keys == items + tweaks:
                return '2.4.0'

        return '2.5.0'

    def migrate(state, version, cls=None):
        for migration in get_migrations(version, args.target, cls=cls):
            if migration.regression:
                print("Regression Notice:", inspect.getdoc(migration),
                      file=sys.stderr)
            state = migration(state)
        return state

    @classmethod
    def setstate(cls, state):
        state, version = state
        state = migrate(state, version, cls=cls)
        cls.__getstate__ = lambda _: (state, args.target)

    for cls in migratables:
        cls.__setstate__ = setstate

    state = pickle.load(args.input)

    # Handle older top-level state change
    version = get_version(state)
    state = migrate(state, version)

    pickle.dump(state, args.output, protocol=pickle.HIGHEST_PROTOCOL)


def add_subparsers(parser):

    def add_say_parser(subparsers):
        parser = subparsers.add_parser(
            'say', usage='[-h] --key KEY [--kwargs KWARGS ...] [input]',
            description="Manually interact with Cleverbot.",
            argument_default=argparse.SUPPRESS,
            help="manually interact with Cleverbot")
        parser.add_argument('input', nargs='?',
                            help="what to say to Cleverbot")
        if 'CLEVERBOT_KEY' in os.environ:
            kwargs = {'default': os.environ['CLEVERBOT_KEY']}
        else:
            kwargs = {'required': True}
        parser.add_argument('--key', help="your API key", **kwargs)

    def add_migrate_parser(subparsers):
        parser = subparsers.add_parser(
            'migrate', description="Migrate a pickled Cleverbot instance.",
            help="migrate a pickled Cleverbot instance")
        parser.add_argument('input', type=argparse.FileType('rb'),
                            help="the file to migrate from")
        parser.add_argument('-t', '--target', default=cleverbot.__version__,
                            type=lambda version: str(StrictVersion(version)),
                            help="the target migration version")
        parser.add_argument('-o', '--output', type=argparse.FileType('wb'),
                            required=True,
                            help="the file to save the migration to")

    subparsers = parser.add_subparsers(
        title='subcommands', parser_class=KwargsParser,
        action=SubParsersAction)
    add_say_parser(subparsers)
    add_migrate_parser(subparsers)


def create_parser():
    parser = argparse.ArgumentParser(
        prog='cleverbot',
        description="A CLI tool to interact with the Cleverbot API.",
        argument_default=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='version',
                        version="cleverbot.py " + cleverbot.__version__)
    parser.add_argument('--key', default=os.environ.get('CLEVERBOT_KEY'),
                        help="your API key")
    parser.add_argument('--cs', help="the cleverbot state")
    parser.add_argument('--timeout', type=float, help="the timeout")
    help = "Cleverbot's mood from {} to {} (0 to 100)"
    parser.add_argument('--tweak1', type=float,
                        help=help.format('sensible', 'wacky'))
    parser.add_argument('--tweak2', type=float,
                        help=help.format('shy', 'talkative'))
    parser.add_argument('--tweak3', type=float,
                        help=help.format('self-centred', 'attentive'))
    return parser


def main():
    parser = create_parser()
    parser.func = core

    # The "hack" below breaks the default help command for sub-commands
    if '-' in parser.prefix_chars:
        default_prefix = '-'
    else:
        default_prefix = parser.prefix_chars[0]
    help_strings = [default_prefix + 'h', default_prefix * 2 + 'help']
    if any(help_string in sys.argv for help_string in help_strings):
        add_subparsers(parser)
        parser.parse_args()
        return

    # Python 2 compatibility
    args, argv = parser.parse_known_args()
    if argv:
        add_subparsers(parser)
        args = parser.parse_args(namespace=args)

    try:
        parser.func(parser, args)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
