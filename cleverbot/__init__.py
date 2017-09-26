__all__ = ['Cleverbot', 'CleverbotError', 'APIError', 'DecodeError', 'Timeout']
__version__ = '1.3.0'

from .cleverbot import Cleverbot
from .errors import CleverbotError, APIError, DecodeError, Timeout
