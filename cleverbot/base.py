import pickle
import weakref

from .migrations import migratable
from .utils import (GenericUnpickler, convo_property, ensure_file, get_slots,
                    keyword_only)


class AttributeMixin(object):

    __slots__ = ()

    url = 'https://www.cleverbot.com/getreply'

    def __getattr__(self, attr):
        """Allow access to the stored data through attributes."""
        try:
            return self.data[attr]
        except KeyError:
            message = "{!r} object has no attribute {!r}"
            raise AttributeError(message.format(type(self).__name__, attr))

    @property
    def cs(self):
        return self.data.get('cs')

    @cs.setter
    def cs(self, value):
        self.data['cs'] = value

    @cs.deleter
    def cs(self):
        self.data.pop('cs', None)


@migratable
class CleverbotBase(AttributeMixin):
    """Base class for Cleverbot."""

    @keyword_only('cs')
    def __init__(self, key, cs=None, timeout=None, tweak1=None, tweak2=None,
                 tweak3=None):
        self.key = key
        self.data = {}
        if cs is not None:
            self.data['cs'] = cs
        self.timeout = timeout
        self.tweak1 = tweak1
        self.tweak2 = tweak2
        self.tweak3 = tweak3
        self.conversations = None

    def __getstate__(self):
        state = vars(self).copy()
        convos = self.conversations
        if isinstance(convos, weakref.WeakSet):
            state['conversations'] = set(convos)
        del state['session']
        return state

    def __setstate__(self, state):
        convos = state['conversations']
        if isinstance(convos, set):
            state['conversations'] = weakref.WeakSet(convos)

        self.__init__(None)  # Set the session
        vars(self).update(state)
        if convos is None:
            return

        if isinstance(convos, dict):
            convos = convos.values()
        for convo in convos:
            convo.session = self.session

    def __copy__(self):
        cleverbot = self.__new__(type(self))
        vars(cleverbot).update(vars(self))
        return cleverbot

    def conversation(self, name, convo):
        """Initialize conversations if necessary and add the conversation to
        it.
        """
        if self.conversations is None:
            self.conversations = {} if name is not None else weakref.WeakSet()
        if name is not None:
            message = "Can't mix named conversations with nameless ones"
            assert isinstance(self.conversations, dict), message
            self.conversations[name] = convo
        else:
            message = "Can't mix nameless conversations with named ones"
            assert isinstance(self.conversations, weakref.WeakSet), message
            self.conversations.add(convo)

    def reset(self):
        """Reset Cleverbot's stored data and all of its conversations."""
        self.data = {}
        convos = self.conversations
        if convos is None:
            return

        if isinstance(convos, dict):
            convos = convos.values()
        for convo in convos:
            convo.reset()

    def save(self, file):
        """Save Cleverbot and all of its conversations into the specified file
        object.

        Arguments:
            file: A filename or a file object that accepts bytes to save the
                data to.
        """
        with ensure_file(file, 'wb') as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)

    def load(self, file):
        """Load and replace Cleverbot's conversations with the previously saved
        conversations from the file.

        Arguments:
            file: The filename or file object to load the saved conversations
                from.
        """
        cleverbot = load(type(self).__module__, file)
        self.data = cleverbot.data
        convos = cleverbot.conversations
        self.conversations = convos
        if convos is None:
            return

        if isinstance(convos, dict):
            convos = convos.values()
        for convo in convos:
            convo.cleverbot = self
            convo.session = self.session


@migratable
class ConversationBase(AttributeMixin):
    """Base class for Conversation."""

    __slots__ = ('__weakref__', 'cleverbot', 'data', '_key', '_timeout',
                 '_tweak1', '_tweak2', '_tweak3', 'session')

    key = convo_property('key')
    timeout = convo_property('timeout')
    tweak1 = convo_property('tweak1')
    tweak2 = convo_property('tweak2')
    tweak3 = convo_property('tweak3')

    @keyword_only('key')
    def __init__(self, cleverbot, key=None, cs=None, timeout=None, tweak1=None,
                 tweak2=None, tweak3=None):
        self.cleverbot = cleverbot
        self.data = {}
        for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
            value = locals()[item]
            if value is not None:
                setattr(self, item, value)
        self.session = cleverbot.session

    def __getstate__(self):
        return {item: getattr(self, item) for item in get_slots(type(self))
                if hasattr(self, item) and item != 'session'}

    def __setstate__(self, state):
        for item, value in state.items():
            setattr(self, item, value)

    def __copy__(self):
        convo = self.__new__(type(self))
        for item in get_slots(type(self)):
            if hasattr(self, item):
                setattr(convo, item, getattr(self, item))
        return convo

    def reset(self):
        self.data = {}


class SayMixinBase(object):

    __slots__ = ()

    def _get_params(self, input, kwargs):
        params = {
            'key': self.key,
            'input': input,
            'cs': self.data.get('cs'),
            'cb_settings_tweak1': self.tweak1,
            'cb_settings_tweak2': self.tweak2,
            'cb_settings_tweak3': self.tweak3,
            'wrapper': 'cleverbot.py'
        }
        for tweak in ('tweak1', 'tweak2', 'tweak3'):
            if tweak not in kwargs:
                continue
            setting = 'cb_settings_' + tweak
            if setting in kwargs:
                message = "Supplied both {!r} and {!r}"
                raise TypeError(message.format(tweak, setting))
            kwargs[setting] = kwargs.pop(tweak)
        params.update(kwargs)
        # aiohttp doesn't filter None values
        return {key: value for key, value in params.items()
                if value is not None}


def load(module, file):
    with ensure_file(file, 'rb') as file:
        return GenericUnpickler(file, module=module).load()
