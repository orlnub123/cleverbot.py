__version__ = '2.5.0'

# Fix for circular import
from . import migrations

from .cleverbot import Cleverbot, load
from .errors import CleverbotError, APIError, DecodeError, Timeout
