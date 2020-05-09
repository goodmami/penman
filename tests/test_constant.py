
import pytest

from penman.exceptions import ConstantError
from penman.constant import (
    SYMBOL,
    STRING,
    INTEGER,
    FLOAT,
    NULL,
    type,
    evaluate,
    quote,
)


def test_type():
    assert type(None) == NULL
    assert type('') == NULL
    assert type('""') == STRING
    assert type('a') == SYMBOL
    assert type('"a"') == STRING
    assert type('"1"') == STRING
    assert type('"escapes \\" and spaces"') == STRING
    assert type('1') == INTEGER
    assert type('1.5') == FLOAT
    assert type('1e-3') == FLOAT


def test_evaluate():
    assert evaluate(None) is None
    assert evaluate('') is None
    assert evaluate('""') == ''
    assert evaluate('a') == 'a'
    assert evaluate('"a"') == 'a'
    assert evaluate('"1"') == '1'
    assert evaluate('"escapes \\" and spaces"') == 'escapes " and spaces'
    assert evaluate('1') == 1
    assert evaluate('1.5') == 1.5
    assert evaluate('1e-3') == 0.001

    # make sure these don't get converted
    assert evaluate('.1') == '.1'
    assert evaluate('true') == 'true'
    assert evaluate('false') == 'false'
    assert evaluate('null') == 'null'
    assert evaluate('NaN') == 'NaN'
    assert evaluate('Infinity') == 'Infinity'
    assert evaluate('+Infinity') == '+Infinity'
    assert evaluate('-Infinity') == '-Infinity'

    with pytest.raises(ConstantError):
        evaluate('"a')
    with pytest.raises(ConstantError):
        evaluate('a"')
    with pytest.raises(ConstantError):
        evaluate('{"a":1}')
    with pytest.raises(ConstantError):
        evaluate('[1]')


def test_quote():
    assert quote(None) == '""'
    assert quote('') == '""'
    assert quote('a') == '"a"'
    assert quote('"a"') == r'"\"a\""'
    assert quote(1) == '"1"'
    assert quote(1.5) == '"1.5"'
