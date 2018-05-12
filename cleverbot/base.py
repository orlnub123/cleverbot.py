import pickle

from .utils import convo_property, error_on_kwarg


class AttributeMixin(object):

    url = 'https://www.cleverbot.com/getreply'

    def __getattr__(self, attr):
        """Allow access to the stored data through attributes."""
        try:
            return self.data[attr]
        except KeyError:
            message = "{0!r} object has no attribute {1!r}"
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
            file: A file object that accepts bytes to save the data to.
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
                for item in filter(lambda item: item in vars(convo), items):
                    convo_dict[item] = vars(convo)[item]
                obj[1].append(convo_dict)
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)

    def load(self, file):
        """Load and replace Cleverbot's conversations with the previously saved
        conversations from the file.

        Arguments:
            file: The file object to load the saved conversations from.
        """
        self.conversations = None
        convos_kwargs = pickle.load(file)[1]
        for convo_kwargs in convos_kwargs:
            self.conversation(**convo_kwargs)


class ConversationBase(AttributeMixin):
    """Base class for Conversation."""

    def __init__(self, cleverbot, **kwargs):
        self.cleverbot = cleverbot
        self.data = {}
        items = ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3')
        for item in filter(lambda item: item in kwargs, items):
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
        tweaks = ('tweak1', 'tweak2', 'tweak3')
        for tweak in filter(lambda tweak: tweak in kwargs, tweaks):
            setting = 'cb_settings_' + tweak
            if setting in kwargs:
                message = "Supplied both {0!r} and {1!r}"
                raise TypeError(message.format(tweak, setting))
            kwargs[setting] = kwargs.pop(tweak)
        params.update(kwargs)
        # aiohttp doesn't filter None values
        return dict(filter(lambda item: item[1] is not None, params.items()))


def load(cleverbot_class, file):
    cleverbot_kwargs, convos_kwargs = pickle.load(file)
    cleverbot = cleverbot_class(**cleverbot_kwargs)
    for convo_kwargs in convos_kwargs:
        cleverbot.conversation(**convo_kwargs)
    return cleverbot
