"""
Functions for basic reading and writing of PENMAN graphs.

NOTE: This module is now deprecated and will be removed in a future
version. Its functions are now available in the penman module.
"""

import warnings

from penman.codec import (  # noqa: F401
    _decode as decode,
    _dump as dump,
    _dumps as dumps,
    _encode as encode,
    _iterdecode as iterdecode,
    _load as load,
    _loads as loads,
)

warnings.warn(
    'The penman.interface module is deprecated. Use the functions from '
    'the penman module directly, e.g., penman.decode().',
    DeprecationWarning,
    stacklevel=2,
)
