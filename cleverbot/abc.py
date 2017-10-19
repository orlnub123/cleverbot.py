from __future__ import absolute_import

import abc


class CleverbotBase:
    """Base class for Cleverbot."""

    url = 'https://www.cleverbot.com/getreply'

    def __getattribute__(self, attr):
        """Allow access to the stored data through attributes."""
        try:
            return super(CleverbotBase, self).__getattribute__(attr)
        except AttributeError as error:
            try:
                return super(
                    CleverbotBase, self).__getattribute__('data')[attr]
            except KeyError:
                raise error

    def __setattr__(self, attr, value):
        """Allow modifying the cleverbot state with an attribute."""
        if attr == 'cs':
            self.data['cs'] = value
        else:
            super(CleverbotBase, self).__setattr__(attr, value)

    @abc.abstractmethod
    def say(self):
        pass

    def reset(self):
        """Reset all of Cleverbot's stored data."""
        self.data = {}


CleverbotBase = abc.ABCMeta('CleverbotBase', (), dict(CleverbotBase.__dict__))
