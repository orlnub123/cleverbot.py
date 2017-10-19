import asyncio

import aiohttp

from .. import __version__
from ..abc import CleverbotBase
from ..errors import APIError, DecodeError, Timeout


class Cleverbot(CleverbotBase):
    """An asynchronous Cleverbot API wrapper."""

    def __init__(self, key, *, cs=None, timeout=None, loop=None):
        """Initialize Cleverbot with the given arguments.

        Arguments:
            key: The key argument is always required. It is your API key.
            cs: The cs argument stands for "cleverbot state". It is the encoded
                state of the conversation so far and includes the whole
                conversation history up to that point.
            timeout: How many seconds to wait for the API to send data before
                giving up and raising an error.
            loop: The event loop used for the asynchronous requests.
        """
        self.key = key
        self.data = {}
        if cs is not None:
            self.data['cs'] = cs
        self.timeout = timeout
        loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession(loop=loop)

    @asyncio.coroutine
    def say(self, input=None, **kwargs):
        """Talk to Cleverbot.

        Arguments:
            input: The input argument is what you want to say to Cleverbot,
                such as "hello".
            **kwargs: Keyword arguments to update the request parameters with.

        Returns:
            Cleverbot's reply.

        Raises:
            APIError: A Cleverbot API error occurred.
                401: Unauthorised due to invalid API key.
                404: API not found.
                413: Request too large if you send a request over 16KB.
                502 or 504: Unable to get reply from API server, please contact
                    us.
                503: Too many requests from a single IP address or API key.
            DecodeError: An error occurred while reading the reply.
            Timeout: The request timed out.
        """
        params = {
            'key': self.key,
            'wrapper': 'cleverbot.py'
        }
        if input is not None:
            params['input'] = input
        try:
            params['cs'] = self.data['cs']
        except KeyError:
            pass
        if kwargs:
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
                    return data['output']
                else:
                    raise APIError(data['error'], data['status'])
        finally:
            reply.release()

    def close(self):
        """Close the connection to the API."""
        self.session.close()
