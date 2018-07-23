import contextlib
import functools
import inspect
import pickle
import sys
from distutils.version import StrictVersion

from .migrations import migrations


class GenericUnpickler(pickle.Unpickler, object):  # Old-style class on py2

    def __init__(self, *args, **kwargs):
        module = kwargs.pop('module')
        super(GenericUnpickler, self).__init__(*args, **kwargs)
        self.__module = module

    def find_class(self, module, name):
        if (name in ('Cleverbot', 'Conversation') and
                module.split('.')[0] == 'cleverbot'):
            module = self.__module
        return super(GenericUnpickler, self).find_class(module, name)


def keyword_only(kwonly_start):
    def decorator(func):
        if sys.version_info.major == 2:
            args, _, _, defaults = inspect.getargspec(func)
        else:
            args, _, _, defaults = inspect.getfullargspec(func)[:4]
        kwonly_index = args.index(kwonly_start)
        required_kwonly_args = set(args[kwonly_index:-len(defaults)])

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) > kwonly_index:
                raise TypeError(
                    "{}() takes {} positional arguments but {} were given"
                    .format(func.__name__, kwonly_index, len(args)))

            missing = required_kwonly_args.difference(kwargs)
            if missing:
                raise TypeError(
                    "{}() missing {} required keyword-only arguments: {}"
                    .format(func.__name__, len(missing),
                            ', '.join(map(repr, missing))))

            return func(*args, **kwargs)

        return wrapper
    return decorator


def convo_property(name):
    _name = '_' + name
    getter = lambda self: getattr(self, _name, getattr(self.cleverbot, name))
    setter = lambda self, value: setattr(self, _name, value)
    deleter = lambda self: delattr(self, _name)
    return property(getter, setter, deleter)


@contextlib.contextmanager
def ensure_file(file, *args, **kwargs):
    if isinstance(file, str):
        file = open(file, *args, **kwargs)
        yield file
        file.close()
        return
    yield file


def get_slots(cls):
    slots = set()
    for cls in cls.__mro__:
        if not hasattr(cls, '__slots__'):
            slots.add('__dict__')
            continue

        if isinstance(cls.__slots__, str):
            cls_slots = [cls.__slots__]
        else:
            cls_slots = cls.__slots__
        for member in cls_slots:
            if member == '__weakref__':
                continue

            if member.startswith('__') and not member.endswith('__'):
                stripped = cls.__name__.lstrip('_')
                if stripped:
                    member = '_{}{}'.format(stripped, member)
            slots.add(member)
    return slots


def get_migrations(version, target, cls=None):
    version, target = map(StrictVersion, [version, target])
    if version == target:
        return []

    if cls is not None:
        for migratable, cls_migrations in migrations.items():
            if migratable is not None and issubclass(cls, migratable):
                break
        else:
            return []
    else:
        cls_migrations = migrations[None]

    target_migrations = []
    downgrade = target < version
    for migration_version, types in cls_migrations.items():
        if downgrade:
            if migration_version > target and migration_version <= version:
                try:
                    target_migrations.append(types['downgrade'])
                except KeyError:
                    pass
        else:
            if migration_version <= target and migration_version > version:
                try:
                    target_migrations.append(types['upgrade'])
                except KeyError:
                    pass
    if downgrade:
        target_migrations.reverse()
    return target_migrations
