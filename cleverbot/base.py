import pickle


class AttributeMixin(object):

    url = 'https://www.cleverbot.com/getreply'

    def __getattr__(self, attr):
        """Allow access to the stored data through attributes."""
        try:
            return self.data[attr]
        except KeyError:
            message = "{0!r} object has no attribute {1!r}"
            raise AttributeError(message.format(self.__class__.__name__, attr))

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
        if kwargs:
            message = "__init__() got an unexpected keyword argument {0!r}"
            raise TypeError(message.format(next(iter(kwargs))))

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
                for item in ('key', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
                    try:
                        convo_dict[item] = convo.__dict__[item]
                    except KeyError:
                        pass
                obj[1].append(convo_dict)
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)

    def load(self, file):
        """Load and replace Cleverbot's conversations with the previously saved
        conversations from the file.

        Arguments:
            file: The file object to load the saved conversations from.
        """
        convos = pickle.load(file)[1]
        self.conversations = None
        for convo_kwargs in convos:
            self.conversation(**convo_kwargs)


class ConversationBase(AttributeMixin):
    """Base class for Conversation."""

    def __init__(self, cleverbot, **kwargs):
        self.cleverbot = cleverbot
        self.data = {}
        for item in ('key', 'cs', 'timeout', 'tweak1', 'tweak2', 'tweak3'):
            if item in kwargs:
                setattr(self, item, kwargs.pop(item))
        self.session = cleverbot.session
        if kwargs:
            message = "__init__() got an unexpected keyword argument {0!r}"
            raise TypeError(message.format(next(iter(kwargs))))

    @property
    def key(self):
        return self.__dict__.get('key', self.cleverbot.key)

    @key.setter
    def key(self, value):
        self.__dict__['key'] = value

    @property
    def timeout(self):
        return self.__dict__.get('timeout', self.cleverbot.timeout)

    @timeout.setter
    def timeout(self, value):
        self.__dict__['timeout'] = value

    @property
    def tweak1(self):
        return self.__dict__.get('tweak1', self.cleverbot.tweak1)

    @tweak1.setter
    def tweak1(self, value):
        self.__dict__['tweak1'] = value

    @property
    def tweak2(self):
        return self.__dict__.get('tweak2', self.cleverbot.tweak2)

    @tweak2.setter
    def tweak2(self, value):
        self.__dict__['tweak2'] = value

    @property
    def tweak3(self):
        return self.__dict__.get('tweak3', self.cleverbot.tweak3)

    @tweak3.setter
    def tweak3(self, value):
        self.__dict__['tweak3'] = value

    def reset(self):
        self.data = {}
