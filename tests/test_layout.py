
import pytest

from penman.exceptions import LayoutError
from penman.model import Model
from penman.tree import Tree
from penman.graph import Graph
from penman.codec import PENMANCodec
from penman.layout import (
    interpret,
    rearrange,
    configure,
    reconfigure,
    has_valid_layout,
    get_pushed_variable,
    appears_inverted,
)


codec = PENMANCodec()
model = Model()


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


def test_rearrange():
    t = codec.parse('''
        (a / alpha
           :ARG0 (b / beta
                    :ARG0 (g / gamma)
                    :ARG1 (d / delta))
           :ARG0-of d
           :ARG1 (e / epsilon))''')

    rearrange(t, model.original_order)
    assert codec.format(t) == (
        '(a / alpha\n'
        '   :ARG0 (b / beta\n'
        '            :ARG0 (g / gamma)\n'
        '            :ARG1 (d / delta))\n'
        '   :ARG0-of d\n'
        '   :ARG1 (e / epsilon))')

    import random; random.seed(1)
    rearrange(t, model.random_order)
    assert codec.format(t) == (
        '(a / alpha\n'
        '   :ARG0-of d\n'
        '   :ARG1 (e / epsilon)\n'
        '   :ARG0 (b / beta\n'
        '            :ARG0 (g / gamma)\n'
        '            :ARG1 (d / delta)))')

    rearrange(t, model.canonical_order)
    assert codec.format(t) == (
        '(a / alpha\n'
        '   :ARG0 (b / beta\n'
        '            :ARG0 (g / gamma)\n'
        '            :ARG1 (d / delta))\n'
        '   :ARG1 (e / epsilon)\n'
        '   :ARG0-of d)')


def test_configure(amr_model):
    g = codec.decode('(a / A)')
    assert configure(g) == Tree(('a', [('/', 'A')]))
    with pytest.raises(LayoutError):
        configure(g, top='A')

    g = codec.decode('(a / A :consist-of (b / B))')
    assert configure(g) == Tree(
        ('a', [('/', 'A'),
               (':consist-of', ('b', [('/', 'B')]))]))
    assert configure(g, top='b') == Tree(
        ('b', [('/', 'B'),
               (':consist', ('a', [('/', 'A')]))]))

    amr_codec = PENMANCodec(model=amr_model)
    g = amr_codec.decode('(a / A :consist-of (b / B))')
    assert configure(g, model=amr_model) == Tree(
        ('a', [('/', 'A'),
               (':consist-of', ('b', [('/', 'B')]))]))
    assert configure(g, top='b', model=amr_model) == Tree(
        ('b', [('/', 'B'),
               (':consist-of-of', ('a', [('/', 'A')]))]))


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
    assert configure(g) == Tree(
        ('t', [('/', 'think'),
               (':ARG0', ('i', [('/', 'i')])),
               (':ARG1', ('f', [('/', 'fail'),
                                (':ARG0', ('y', [('/', 'you')])),
                                (':ARG1', ('a', [('/', 'act'),
                                                 (':polarity', '-'),
                                                 (':polarity', '-')]))]))]))


def test_get_pushed_variable():
    g = codec.decode('''
        (a / alpha
           :ARG0 (b / beta)
           :ARG1-of (g / gamma))''')
    assert get_pushed_variable(g, ('a', ':instance', 'alpha')) is None
    assert get_pushed_variable(g, ('a', ':ARG0', 'b')) == 'b'
    assert get_pushed_variable(g, ('g', ':ARG1', 'a')) == 'g'


def test_appears_inverted():
    g = codec.decode('''
        (a / alpha
           :ARG0 (b / beta)
           :ARG1-of (g / gamma))''')
    assert not appears_inverted(g, ('a', ':instance', 'alpha'))
    assert not appears_inverted(g, ('a', ':ARG0', 'b'))
    assert appears_inverted(g, ('g', ':ARG1', 'a'))
