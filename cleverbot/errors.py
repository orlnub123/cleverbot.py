class CleverbotError(Exception):
    """Base class for all Cleverbot errors."""


class APIError(CleverbotError):
    """Raised when a Cleverbot API error occurs. See the official Cleverbot
    documentation for an updated list of all the possible errors.
    """

    def __init__(self, error=None, status=None):
        message = "An unspecified error occurred"
        super(APIError, self).__init__(error if error is not None else message)
        self.error = error
        self.status = status


class DecodeError(CleverbotError):
    """Raised when a decode error occurs while reading the reply. Reset
    Cleverbot or the respective conversation to fix it.
    """


class Timeout(CleverbotError):
    """Raised when the request takes longer than the specified time."""

    def __init__(self, timeout=None):
        if timeout is not None:
            message = "Request timed out after {} seconds".format(timeout)
        else:
            message = "Request timed out"
        super(Timeout, self).__init__(message)
        self.timeout = timeout
