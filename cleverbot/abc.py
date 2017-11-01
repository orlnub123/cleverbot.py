from __future__ import absolute_import

import abc


class CleverbotBase(abc.ABCMeta('ABC', (), {})):  # Python 2 compatibility
    """Base class for Cleverbot."""

    url = 'https://www.cleverbot.com/getreply'

    def __getattr__(self, attr):
        """Allow access to the stored data through attributes."""
        try:
            return self.data[attr]
        except KeyError:
            message = "'{0}' object has no attribute '{1}'"
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

    @abc.abstractmethod
    def say(self):
        pass

    def reset(self):
        """Reset all of Cleverbot's stored data."""
        self.data = {}
