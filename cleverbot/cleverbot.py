import requests

from . import __version__
from .abc import CleverbotBase
from .errors import APIError, DecodeError, Timeout


class Cleverbot(CleverbotBase):
    """A Cleverbot API wrapper."""

    def __init__(self, key, **kwargs):  # Python 2 compatible keyword-only args
        """Initialize Cleverbot with the given arguments.

        Arguments:
            key: The key argument is always required. It is your API key.
            cs: The cs argument stands for "cleverbot state". It is the encoded
                state of the conversation so far and includes the whole
                conversation history up to that point.
            timeout: How many seconds to wait for the API to send data before
                giving up and raising an error.
        """
        self.key = key
        self.data = {}
        if 'cs' in kwargs:
            self.data['cs'] = kwargs.pop('cs')
        self.timeout = kwargs.pop('timeout', None)
        self.session = requests.Session()
        if kwargs:
            message = "__init__() got an unexpected keyword argument '{0}'"
            raise TypeError(message.format(next(iter(kwargs))))

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
                Status codes:
                    401: Unauthorised due to invalid API key.
                    404: API not found.
                    413: Request too large if you send a request over 64Kb.
                    502 or 504: Unable to get reply from API server, please
                        contact us.
                    503: Too many requests from a single IP address or API key.
            DecodeError: An error occurred while reading the reply.
            Timeout: The request timed out.
        """
        params = {
            'key': self.key,
            'input': input,
            'cs': self.data.get('cs'),
            'wrapper': 'cleverbot.py'
        }
        if kwargs:
            params.update(kwargs)

        headers = {
            'User-Agent': 'cleverbot.py/' + __version__ + ' '
            '(+https://github.com/orlnub123/cleverbot.py)'
        }
        try:
            reply = self.session.get(
                self.url, params=params, headers=headers, timeout=self.timeout)
        except requests.Timeout:
            raise Timeout(self.timeout)
        else:
            try:
                data = reply.json()
            except ValueError as error:
                raise DecodeError(error)
            else:
                if reply.status_code == 200:
                    self.data = data
                    return data['output']
                else:
                    raise APIError(data['error'], data['status'])

    def close(self):
        """Close the connection to the API."""
        self.session.close()
