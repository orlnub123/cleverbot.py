__all__ = ['CleverbotError', 'APIError', 'DecodeError', 'Timeout']

from requests.exceptions import HTTPError, Timeout


class CleverbotError(Exception):
    """Base class for all Cleverbot errors."""


class APIError(CleverbotError, HTTPError):
    """Raised when a Cleverbot API error occurs.

    Errors:
        401: Unauthorised due to invalid API key.
        404: API not found.
        413: Request too large if you send a request over 16KB.
        502 or 504: Unable to get reply from API server, please contact us.
        503: Too many requests from a single IP address or API key.
    """

    def __init__(self, error):
        super(Exception, self).__init__(error)


class DecodeError(CleverbotError, ValueError):
    """Raised when a decode error occurs while reading the reply.

    This shouldn't happen.
    """

    def __init__(self, error):
        super(Exception, self).__init__(error)


class Timeout(CleverbotError, Timeout):
    """Raised when the request times out."""

    def __init__(self, timeout):
        super(Exception, self).__init__(
            "Request timed out after {} seconds.".format(timeout))
