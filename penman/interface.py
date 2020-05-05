
"""
Functions for basic reading and writing of PENMAN graphs.

NOTE: This module is now deprecated and will be removed in a future
version. Its functions are now available in the penman module.
"""

import warnings

from penman.codec import (  # noqa: F401
    _decode as decode,
    _iterdecode as iterdecode,
    _encode as encode,
    _load as load,
    _loads as loads,
    _dump as dump,
    _dumps as dumps,
)

warnings.warn(
    'The penman.interface module is deprecated. Use the functions from '
    'the penman module directly, e.g., penman.decode().',
    DeprecationWarning)
