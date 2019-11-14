
import pytest

from penman.exceptions import LayoutError
from penman.model import Model
from penman.tree import Tree
from penman.graph import Graph
from penman.codec import PENMANCodec
from penman.layout import (
    interpret,
    configure,
    reconfigure,
    has_valid_layout,
)


codec = PENMANCodec()


@pytest.fixture(scope='module')
def amr_model(mini_amr):
    return Model.from_dict(mini_amr)


def test_interpret(amr_model):
    t = codec.parse('(a / A)')
    assert interpret(t) == Graph([('a', ':instance', 'A')], top='a')

    t = codec.parse('(a / A :consist-of (b / B))')
    assert interpret(t) == Graph(
        [('a', ':instance', 'A'),
         ('b', ':consist', 'a'),
         ('b', ':instance', 'B')],
        top='a')
    assert interpret(t, model=amr_model) == Graph(
        [('a', ':instance', 'A'),
         ('a', ':consist-of', 'b'),
         ('b', ':instance', 'B')],
        top='a')


def test_configure(amr_model):
    g = codec.decode('(a / A)')
    assert configure(g) == Tree(('a', [('/', 'A', [])]))
    with pytest.raises(LayoutError):
        configure(g, top='A')

    g = codec.decode('(a / A :consist-of (b / B))')
    assert configure(g) == Tree(
        ('a', [
            ('/', 'A', []),
            (':consist-of', ('b', [('/', 'B', [])]), [])
        ])
    )
    assert configure(g, top='b') == Tree(
        ('b', [
            ('/', 'B', []),
            (':consist', ('a', [('/', 'A', [])]), [])
        ])
    )

    amr_codec = PENMANCodec(model=amr_model)
    g = amr_codec.decode('(a / A :consist-of (b / B))')
    assert configure(g, model=amr_model) == Tree(
        ('a', [
            ('/', 'A', []),
            (':consist-of', ('b', [('/', 'B', [])]), [])
        ])
    )
    assert configure(g, top='b', model=amr_model) == Tree(
        ('b', [
            ('/', 'B', []),
            (':consist-of-of', ('a', [('/', 'A', [])]), [])
        ])
    )

