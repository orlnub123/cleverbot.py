import asyncio
import functools

import aiohttp

from .. import __version__
from ..base import CleverbotBase, ConversationBase, SayMixinBase, load
from ..errors import APIError, DecodeError, Timeout


class SayMixin(SayMixinBase):

    __slots__ = ()

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
        params = self._get_params(input, kwargs)
        try:
            reply = yield from self.session.get(
                self.url, params=params, timeout=self.timeout)
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
        headers = {'User-Agent': 'cleverbot.py/' + __version__ + ' '
                   '(+https://github.com/orlnub123/cleverbot.py)'}
        self.session = aiohttp.ClientSession(loop=loop, headers=headers)

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

    @asyncio.coroutine
    def close(self):
        """Close Cleverbot's connection to the API."""
        yield from self.session.close()


class Conversation(SayMixin, ConversationBase):

    __slots__ = ()


load = functools.partial(load, __name__)
