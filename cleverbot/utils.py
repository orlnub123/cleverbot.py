def error_on_kwarg(func, kwargs):
    if kwargs:
        message = "{0}() got an unexpected keyword argument {1!r}"
        raise TypeError(message.format(func.__name__, next(iter(kwargs))))


def convo_property(name):
    import operator
    getter = lambda self: vars(self).get(name, getattr(self.cleverbot, name))
    setter = lambda self, value: operator.setitem(vars(self), name, value)
    return property(getter, setter)
