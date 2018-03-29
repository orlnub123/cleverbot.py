import asyncio
import pickle

import aiohttp

from .. import __version__
from ..base import CleverbotBase, ConversationBase
from ..errors import APIError, DecodeError, Timeout


class SayMixin:

    @asyncio.coroutine
    def say(self, input=None, **kwargs):
        """Talk to Cleverbot.

        Arguments:
            input: The input argument is what you want to say to Cleverbot,
                such as "hello".
            tweak1-3: Changes Cleverbot's mood.
            **kwargs: Keyword arguments to update the request parameters with.

        Returns:
            Cleverbot's reply.

        Raises:
            APIError: A Cleverbot API error occurred.
            DecodeError: An error occurred while reading the reply.
            Timeout: The request timed out.
        """
        params = {
            'key': self.key,
            'wrapper': 'cleverbot.py'
        }
        # aiohttp doesn't filter None values
        if input is not None:
            params['input'] = input
        try:
            params['cs'] = self.data['cs']
        except KeyError:
            pass
        for tweak in ('tweak1', 'tweak2', 'tweak3'):
            if getattr(self, tweak, None) is not None:
                params['cb_settings_' + tweak] = getattr(self, tweak)
        if kwargs:
            for tweak in ('tweak1', 'tweak2', 'tweak3'):
                setting = 'cb_settings_' + tweak
                if tweak in kwargs and setting not in kwargs:
                    kwargs[setting] = kwargs.pop(tweak)
                elif tweak in kwargs and setting in kwargs:
                    message = "Supplied both {!r} and {!r}"
                    raise TypeError(message.format(tweak, setting))
            # Python 3.4 compatibility
            params.update(kwargs)

        headers = {
            'User-Agent': 'cleverbot.py/' + __version__ + ' '
            '(+https://github.com/orlnub123/cleverbot.py)'
        }
        try:
            reply = yield from self.session.get(
                self.url, params=params, headers=headers, timeout=self.timeout)
        except asyncio.TimeoutError:
            raise Timeout(self.timeout)
        else:
            try:
                data = yield from reply.json()
            except ValueError as error:
                raise DecodeError(error)
            else:
                if reply.status == 200:
                    self.data = data
                    return data.get('output')
                else:
                    raise APIError(data.get('error'), data.get('status'))


class Cleverbot(SayMixin, CleverbotBase):
    """An asynchronous Cleverbot API wrapper."""

    def __init__(self, *args, loop=None, **kwargs):
        """Initialize Cleverbot with the given arguments.

        Arguments:
            key: The key argument is always required. It is your API key.
            cs: The cs argument stands for "cleverbot state". It is the encoded
                state of the conversation so far and includes the whole
                conversation history up to that point.
            timeout: How many seconds to wait for the API to respond before
                giving up and raising an error.
            loop: The event loop used for the asynchronous requests.
        """
        super().__init__(*args, **kwargs)
        loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession(loop=loop)

    def conversation(self, name=None, **kwargs):
        """Make a new conversation.

        Arguments:
            name: The key for the dictionary the conversation will be stored as
                in conversations. If None the conversation will be stored as a
                list instead. Mixing both types results in an error.
            **kwargs: Keyword arguments to pass into the new conversation.
                These accept the same arguments as Cleverbot.

        Returns:
            The new conversation.
        """
        convo = Conversation(self, **kwargs)
        super().conversation(name, convo)
        return convo

    def close(self):
        """Close Cleverbot's connection to the API."""
        self.session.close()


class Conversation(SayMixin, ConversationBase):
    pass


def load(file):
    """Load and return the previously saved Cleverbot with its conversations.

    Arguments:
        file: The file object to load Cleverbot and its conversations from.

    Returns:
        A new Cleverbot instance.
    """
    cleverbot_kwargs, convos = pickle.load(file)
    cleverbot = Cleverbot(**cleverbot_kwargs)
    for convo_kwargs in convos:
        cleverbot.conversation(**convo_kwargs)
    return cleverbot
