import pickle

from .utils import convo_property, ensure_file, error_on_kwarg


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


class CleverbotBase(AttributeMixin):
    """Base class for Cleverbot."""

    def __init__(self, key, **kwargs):  # Python 2 compatible keyword-only args
        self.key = key
        self.data = {}
        if 'cs' in kwargs:
            self.data['cs'] = kwargs.pop('cs')
        self.timeout = kwargs.pop('timeout', None)
        for tweak in ('tweak1', 'tweak2', 'tweak3'):
            setattr(self, tweak, kwargs.pop(tweak, None))
        self.conversations = None
        error_on_kwarg(self.__init__, kwargs)

    def conversation(self, name, convo):
        """Initialize conversations if necessary and add the conversation to
        it.
        """
        if self.conversations is None:
            self.conversations = {} if name is not None else []
        if name is not None:
            message = "Can't mix named conversations with nameless ones"
            assert isinstance(self.conversations, dict), message
            self.conversations[name] = convo
        else:
            message = "Can't mix nameless conversations with named ones"
            assert isinstance(self.conversations, list), message
            self.conversations.append(convo)

    def reset(self):
        """Reset Cleverbot's stored data and all of its conversations."""
        self.data = {}
        for convo in self.conversations:
            if isinstance(self.conversations, dict):
                convo = self.conversations[convo]
            convo.reset()

    def save(self, file):
        """Save Cleverbot and all of its conversations into the specified file
        object.

        Arguments:
            file: A filename or a file object that accepts bytes to save the
                data to.
        """
        obj = ({'key': self.key, 'cs': self.cs, 'timeout': self.timeout,
                'tweak1': self.tweak1, 'tweak2': self.tweak2,
                'tweak3': self.tweak3}, [])
        if self.conversations is not None:
            for convo in self.conversations:
                if isinstance(self.conversations, dict):
                    name, convo = convo, self.conversations[convo]
                    convo_dict = {'name': name, 'cs': convo.data.get('cs')}
                else:
                    convo_dict = {'cs': convo.data.get('cs')}
                items = ('key', 'timeout', 'tweak1', 'tweak2', 'tweak3')
                _items = ('_' + item for item in items)
                for item, _item in zip(items, _items):
                    if hasattr(convo, _item):
                        convo_dict[item] = getattr(convo, _item)
                obj[1].append(convo_dict)
        with ensure_file(file, 'wb') as file:
            pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)

    def load(self, file):
        """Load and replace Cleverbot's conversations with the previously saved
        conversations from the file.

        Arguments:
            file: The filename or file object to load the saved conversations
                from.
        """
        self.conversations = None
        with ensure_file(file, 'rb') as file:
            convos_kwargs = pickle.load(file)[1]
        for convo_kwargs in convos_kwargs:
            self.conversation(**convo_kwargs)


class ConversationBase(AttributeMixin):
    """Base class for Conversation."""

    __slots__ = ('cleverbot', 'data', '_key', '_timeout', '_tweak1', '_tweak2',
                 '_tweak3', 'session')

    def __init__(self, cleverbot, **kwargs):
        self.cleverbot = cleverbot
        self.data = {}
        for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
            if item in kwargs:
                setattr(self, item, kwargs.pop(item))
        self.session = cleverbot.session
        error_on_kwarg(self.__init__, kwargs)

    def reset(self):
        self.data = {}

    key = convo_property('key')
    timeout = convo_property('timeout')
    tweak1 = convo_property('tweak1')
    tweak2 = convo_property('tweak2')
    tweak3 = convo_property('tweak3')


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


def load(cleverbot_class, file):
    with ensure_file(file, 'rb') as file:
        cleverbot_kwargs, convos_kwargs = pickle.load(file)
    cleverbot = cleverbot_class(**cleverbot_kwargs)
    for convo_kwargs in convos_kwargs:
        cleverbot.conversation(**convo_kwargs)
    return cleverbot
