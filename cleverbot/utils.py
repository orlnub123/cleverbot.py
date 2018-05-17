import contextlib


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
