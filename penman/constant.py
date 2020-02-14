
"""
Functions for working with constant values.
"""

from typing import Union
from enum import Enum
import json

from penman.types import Constant
from penman.exceptions import ConstantError


pytype = type  # store because type() is redefined below


class Type(Enum):
    """
    An enumeration of constant value types.
    """

    SYMBOL = 'Symbol'
    STRING = 'String'
    INTEGER = 'Integer'
    FLOAT = 'Float'
    NULL = 'Null'


# Make them available at the module level
SYMBOL = Type.SYMBOL    #: Symbol constants (e.g., :code:`(... :polarity -)`)
STRING = Type.STRING    #: String constants (e.g., :code:`(... :op1 "Kim")`)
INTEGER = Type.INTEGER  #: Integer constants (e.g., :code:`(... :value 12)`)
FLOAT = Type.FLOAT      #: Float constants (e.g., :code:`(... :value 1.2)`)
NULL = Type.NULL        #: Empty values (e.g., :code:`(... :ARG1 )`)

_typemap = {
    str: SYMBOL,  # needs further checking
    int: INTEGER,
    float: FLOAT,
    type(None): NULL,
}


def type(constant_string: Union[str, None]) -> Type:
    """
    Return the type of constant encoded by *constant_string*.

    Examples:
        >>> from penman import constant
        >>> constant.type('-')
        <Type.SYMBOL: 'Symbol'>
        >>> constant.type('"foo"')
        <Type.STRING: 'String'>
        >>> constant.type('1')
        <Type.INTEGER: 'Integer'>
        >>> constant.type('1.2')
        <Type.FLOAT: 'Float'>
        >>> constant.type('')
        <Type.NULL: 'Null'>
    """
    if constant_string is None:
        typ = NULL
    else:
        assert isinstance(constant_string, str)
        value = evaluate(constant_string)
        typ = _typemap[pytype(value)]
        if (typ == Type.SYMBOL
                and constant_string.startswith('"')
                and constant_string.endswith('"')):
            typ = Type.STRING
    return typ


def evaluate(constant_string: Union[str, None]) -> Constant:
    """
    Evaluate and return *constant_string*.

    If *constant_string* is ``None`` or an empty symbol (``''``), this
    function returns ``None``, while an empty string constant
    (``'""'``) returns an empty :py:class:`str` object
    (``''``). Otherwise, symbols are returned unchanged while strings
    get quotes removed and escape sequences are unescaped. Note that
    this means it is impossible to recover the original type of
    strings and symbols once they have been evaluated. For integer and
    float constants, this function returns the equivalent Python
    :py:class:`int` or :py:class:`float` objects.

    Examples:
        >>> from penman import constant
        >>> constant.evaluate('-')
        '-'
        >>> constant.evaluate('"foo"')
        'foo'
        >>> constant.evaluate('1')
        1
        >>> constant.evaluate('1.2')
        1.2
        >>> constant.evaluate('') is None
        True
    """
    value: Constant = constant_string
    if value is None or value == '':
        value = None
    else:
        assert isinstance(constant_string, str)
        if constant_string.startswith('"') ^ constant_string.endswith('"'):
            raise ConstantError(f'unbalanced quotes: {constant_string}')
        if constant_string not in ('true', 'false', 'null'):
            try:
                value = json.loads(constant_string, parse_constant=str)
            except json.JSONDecodeError:
                value = constant_string

    if not (value is None or isinstance(value, (str, int, float))):
        raise ConstantError(f'invalid constant: {value!r}')

    return value


def quote(constant: Constant) -> str:
    """
    Return *constant* as a quoted string.

    If *constant* is ``None``, this function returns an empty string
    constant (``'""'``). All other types are cast to a string and
    quoted.

    Examples:
        >>> from penman import constant
        >>> constant.quote(None)
        '""'
        >>> constant.quote('')
        '""'
        >>> constant.quote('foo')
        '"foo"'
        >>> constant.quote('"foo"')
        '"\\\\"foo\\\\""'
        >>> constant.quote(1)
        '"1"'
        >>> constant.quote(1.5)
        '"1.5"'
    """
    if constant is None:
        return '""'
    else:
        return json.dumps(str(constant))
