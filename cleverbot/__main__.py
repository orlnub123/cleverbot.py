from __future__ import absolute_import, print_function

import argparse
import getpass
import os
import sys

import cleverbot


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


def add_subparsers(parser):
    subparsers = parser.add_subparsers(
        title='subcommands', parser_class=KwargsParser,
        action=SubParsersAction)
    parser_say = subparsers.add_parser(
        'say', usage='[-h] --key KEY [--kwargs KWARGS ...] [input]',
        description="Manually interact with Cleverbot.",
        argument_default=argparse.SUPPRESS,
        help="manually interact with Cleverbot")
    parser_say.add_argument('input', nargs='?',
                            help="what to say to Cleverbot")
    if 'CLEVERBOT_KEY' in os.environ:
        kwargs = {'default': os.environ['CLEVERBOT_KEY']}
    else:
        kwargs = {'required': True}
    parser_say.add_argument('--key', help="your API key", **kwargs)


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
