import contextlib
import pickle


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


def error_on_kwarg(func, kwargs):
    if kwargs:
        message = "{}() got an unexpected keyword argument {!r}"
        raise TypeError(message.format(func.__name__, next(iter(kwargs))))


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
