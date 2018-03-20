class CleverbotError(Exception):
    """Base class for all Cleverbot errors."""


class APIError(CleverbotError):
    """Raised when a Cleverbot API error occurs. See the official Cleverbot
    documentation for an updated list of all the possible errors.
    """

    def __init__(self, error, status):
        super(APIError, self).__init__(error)
        self.error = error
        self.status = status


class DecodeError(CleverbotError):
    """Raised when a decode error occurs while reading the reply. Reset
    Cleverbot or the respective conversation to fix it.
    """


class Timeout(CleverbotError):
    """Raised when the request takes longer than the specified time."""

    def __init__(self, timeout):
        super(Timeout, self).__init__(
            "Request timed out after {0} seconds".format(timeout))
        self.timeout = timeout
