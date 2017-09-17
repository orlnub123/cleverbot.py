__all__ = ['Cleverbot']

import requests
from .errors import CleverbotError, APIError, DecodeError, Timeout


class Cleverbot(object):
    """A Cleverbot API wrapper."""

    url = 'https://www.cleverbot.com/getreply'

    def __init__(self, key, **kwargs):
        """Initialize Cleverbot with the given arguments.

        Arguments:
            key: The key argument is always required. It is your API key.
            cs: The cs argument stands for "cleverbot state". It is the encoded
                state of the conversation so far and includes the whole
                conversation history up to that point.
            timeout: How many seconds to wait for the API to send data before
                giving up and raising an error.
            loop: The event loop used for asay.
            **kwargs: Keyword arguments to pass into requests.get
        """
        self.key = key
        self.data = {}
        if 'cs' in kwargs:
            self.data['cs'] = kwargs.pop('cs')
        self.timeout = kwargs.pop('timeout', None)
        self.loop = kwargs.pop('loop', None)
        self.kwargs = kwargs

    def __getattr__(self, attr):
        """Allow access to the stored data through attributes."""
        try:
            return self.data[attr]
        except KeyError as error:
            pass
        object.__getattribute__(self, attr)

    def say(self, text, **vtext):
        """Talk to Cleverbot.

        Arguments:
            text: The text argument is what you want to say to Cleverbot, such
                as "hello".
            **vtext: If you wish to override the conversation history, you can
                pass in keyword arguments like vtext2 to override the last
                thing the bot said, vtext3 for the previous thing the user
                said, and so on.

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
            'input': text,
            'wrapper': 'cleverbot.py'
        }
        try:
            params['cs'] = self.data['cs']
        except KeyError:
            pass
        if vtext:
            params.update(vtext)
        return self._query(params)

    def asay(self, *args, **kwargs):
        """Look in _async.py for the actual function."""
        raise CleverbotError("asay requires aiohttp and Python 3.4.2+")

    def reset(self):
        """Reset all of Cleverbot's stored data."""
        self.data = {}

    def _query(self, params):
        """Get Cleverbot's reply and store it in a dictionary.

        Keys:
            cs: State of the conversation so far, which contains an encoded
                copy of the conversation id and history.
            interaction_count: How many pairs of bot/user interactions have
                occurred so far.
            input: The entire user input, with any spaces trimmed off both
                ends.
            output: Cleverbot's reply.
            conversation_id: Identifier for this conversation between user and
                bot.
            errorline: Any error information from Cleverbot, this is different
                from general the general errors described below.
            time_taken: The number of milliseconds the bot took to respond.
            time_elapsed: Approximate number of seconds since conversation
                started.
            interaction_1 to interaction_50: Record of the previous
                interactions. The interaction variables come in pairs. For
                example interaction_1 contains the last thing the user said,
                and interaction_1_other is the bot's reply. interaction_2 was
                the user's previous input and so on. So to read the whole
                conversation in order, you have to display the interaction
                variables in reverse order, eg interaction_5,
                interaction_5_other, interaction_4, interaction_4_other, etc.
                Note that if an interaction didn't occur, the interaction_other
                will not be defined.
        """
        try:
            reply = requests.get(
                self.url, params=params, timeout=self.timeout, **self.kwargs)
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

    try:
        from ._async import asay, _aquery
    except (ImportError, SyntaxError):
        pass
