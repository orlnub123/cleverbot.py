class CleverbotError(Exception):
    """Base class for all Cleverbot errors."""


class APIError(CleverbotError):
    """Raised when a Cleverbot API error occurs.

    Errors:
        401: Unauthorised due to invalid API key.
        404: API not found.
        413: Request too large if you send a request over 16KB.
        502 or 504: Unable to get reply from API server, please contact us.
        503: Too many requests from a single IP address or API key.
    """

    def __init__(self, error, status):
        super(APIError, self).__init__(error)
        self.error = error
        self.status = status


class DecodeError(CleverbotError):
    """Raised when a decode error occurs while reading the reply.

    This shouldn't happen.
    """


class Timeout(CleverbotError):
    """Raised when the request times out after the specified time."""

    def __init__(self, timeout):
        super(Timeout, self).__init__(
            "Request timed out after {} seconds".format(timeout))
        self.timeout = timeout
