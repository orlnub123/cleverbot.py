def error_on_kwarg(func, kwargs):
    if kwargs:
        message = "{0}() got an unexpected keyword argument {1!r}"
        raise TypeError(message.format(func.__name__, next(iter(kwargs))))


def convo_property(name):
    _name = '_' + name
    getter = lambda self: getattr(self, _name, getattr(self.cleverbot, name))
    setter = lambda self, value: setattr(self, _name, value)
    return property(getter, setter)
