
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
    appears_inverted,
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


def test_issue_34():
    # https://github.com/goodmami/penman/issues/34
    g = codec.decode('''
        # ::snt I think you failed to not not act.
        (t / think
           :ARG0 (i / i)
           :ARG1 (f / fail
              :ARG0 (y / you)
              :ARG1 (a / act
                 :polarity -
                 :polarity -)))''')
    print(configure(g))
    assert configure(g) == Tree(
        ('t', [
            ('/', 'think', []),
            (':ARG0', ('i', [('/', 'i', [])]), []),
            (':ARG1', ('f', [
                ('/', 'fail', []),
                (':ARG0', ('y', [('/', 'you', [])]), []),
                (':ARG1', ('a', [
                    ('/', 'act', []),
                    (':polarity', '-', []),
                    (':polarity', '-', [])]),
                 [])]),
             [])]))


def test_appears_inverted():
    g = codec.decode('''
        (a / alpha
           :ARG0 (b / beta)
           :ARG1-of (g / gamma))''')
    assert not appears_inverted(g, ('a', ':instance', 'alpha'))
    assert not appears_inverted(g, ('a', ':ARG0', 'b'))
    assert appears_inverted(g, ('g', ':ARG1', 'a'))
