import collections
import functools
import inspect
import pickle


migrations = collections.defaultdict(
    functools.partial(collections.defaultdict, dict))
migratables = []


def migration(version, cls=None, downgrade=False, regression=False):
    if cls is not None and cls not in migratables:
        raise RuntimeError

    def decorator(func):
        type = 'upgrade' if not downgrade else 'downgrade'
        migrations[cls][version][type] = func
        func.regression = regression
        return func
    return decorator


def migratable(cls):
    migratables.append(cls)
    original_getstate = cls.__getstate__
    original_setstate = cls.__setstate__

    @functools.wraps(cls.__getstate__)
    def getstate(self):
        if hasattr(original_getstate, '__get__'):
            state = original_getstate.__get__(self)()
        else:
            state = original_getstate()
        return (state, __version__)

    @functools.wraps(cls.__setstate__)
    def setstate(self, state):
        state, version = state
        for migration in get_migrations(version, __version__, type(self)):
            if migration.regression:
                raise pickle.UnpicklingError(
                    "Won't implicitly migrate due to a regression: {!r}. "
                    "Force migrate via the CLI. Learn more with `python -m "
                    "cleverbot migrate -h`".format(inspect.getdoc(migration)))
            state = migration(state)
        if hasattr(original_setstate, '__get__'):
            original_setstate.__get__(self)(state)
        else:
            original_setstate(state)

    cls.__getstate__ = getstate
    cls.__setstate__ = setstate
    return cls


# Circular import woes
from . import __version__
from .base import CleverbotBase
from .cleverbot import Cleverbot
from .utils import get_migrations


@migration('2.2.0', downgrade=True, regression=True)
def migrator(state):
    """Tweaks will be lost for Cleverbot and its conversations."""
    for tweak in ('tweak1', 'tweak2', 'tweak3'):
        del state[0][tweak]
        for convo in state[1]:
            if tweak in convo:
                del convo[tweak]
    return state


@migration('2.5.0', regression=True)
def migrator(state):
    """Nameless conversations will be lost."""
    cleverbot_kwargs, convos_kwargs = state
    cb = Cleverbot(**cleverbot_kwargs)
    for convo_kwargs in convos_kwargs:
        cb.conversation(**convo_kwargs)
    return cb


@migration('2.5.0', downgrade=True)
def migrator(cleverbot):
    if not isinstance(cleverbot, CleverbotBase):
        raise RuntimeError("Top-level object needs to be Cleverbot")

    state = cleverbot.__getstate__()[0]
    obj = ({item: state[item] for item in ('key', 'timeout', 'tweak1',
                                           'tweak2', 'tweak3')}, [])
    obj[0]['cs'] = state['data'].get('cs')

    convos = state['conversations']
    if convos is not None:
        for convo in convos:
            if isinstance(convos, dict):
                name, convo = convo, convos[convo]
                convo_dict = {'name': name}
            else:
                convo_dict = {}
            convo_state = convo.__getstate__()[0]
            convo_dict['cs'] = convo_state['data'].get('cs')
            items = ('key', 'timeout', 'tweak1', 'tweak2', 'tweak3')
            _items = ('_' + item for item in items)
            for item, _item in zip(items, _items):
                if _item in convo_state:
                    convo_dict[item] = convo_state[_item]
            obj[1].append(convo_dict)
    return obj
