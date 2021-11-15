
import random
import logging

import pytest

from penman.exceptions import LayoutError
from penman.model import Model
from penman.tree import Tree
from penman.graph import Graph
from penman.codec import PENMANCodec
from penman import layout
from penman.layout import (
    interpret,
    rearrange,
    configure,
    reconfigure,
    get_pushed_variable,
    appears_inverted,
    node_contexts,
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
    random.seed(1)
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


def test_issue_85(monkeypatch, caplog):
    # https://github.com/goodmami/penman/issues/85
    # Emulate multiprocessing by reassigning POP
    with monkeypatch.context() as m:
        m.setattr(layout, 'POP', layout.Pop())
        g = codec.decode('(a / alpha :ARG0 (b / beta))')
    caplog.set_level(logging.WARNING)
    codec.encode(g, indent=None)
    assert 'epigraphical marker ignored: POP' not in caplog.text


def test_reconfigure():
    g = codec.decode('''
        (a / alpha
           :ARG0 b
           :ARG1 (g / gamma
                    :ARG0-of (b / beta)))''')
    # original order reconfiguration puts node definitions at first
    # appearance of a variable
    assert reconfigure(g) == Tree(
        ('a', [('/', 'alpha'),
               (':ARG0', ('b', [('/', 'beta')])),
               (':ARG1', ('g', [('/', 'gamma'),
                                (':ARG0-of', 'b')]))]))
    # canonical order reconfiguration can also shift things like
    # inverted arguments
    assert reconfigure(g, key=model.canonical_order) == Tree(
        ('a', [('/', 'alpha'),
               (':ARG0', ('b', [('/', 'beta'),
                                (':ARG0', ('g', [('/', 'gamma')]))])),
               (':ARG1', 'g')]))


def test_issue_90():
    # https://github.com/goodmami/penman/issues/90

    g = Graph([('i', ':instance', 'iota'),
               ('i2', ':instance', 'i'),
               ('i', ':ARG0', 'i2')],
              top='i')
    assert reconfigure(g) == Tree(
        ('i', [('/', 'iota'),
               (':ARG0', ('i2', [('/', 'i')]))]))


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


def test_issue_47():
    # https://github.com/goodmami/penman/issues/47
    g = codec.decode('''
        (a / alpha
           :ARG0 (b / beta)
           :ARG1 (g / gamma
                    :ARG0 (d / delta)
                    :ARG1-of (e / epsilon)
                    :ARG1-of b))''')
    assert not appears_inverted(g, ('a', ':ARG0', 'b'))
    assert not appears_inverted(g, ('g', ':ARG0', 'd'))
    assert appears_inverted(g, ('e', ':ARG1', 'g'))
    assert appears_inverted(g, ('b', ':ARG1', 'g'))


def test_issue_87():
    # https://github.com/goodmami/penman/issues/87

    # The duplicate triple (i, :ARG0, c) below means the graph is bad
    # so the output is not guaranteed. Just check for errors.
    g = codec.decode('(c / company :ARG0-of (i / insure-02 :ARG0 c))')
    appears_inverted(g, ('i', ':ARG0', 'c'))
    codec.encode(g)
    g = codec.decode('(c / company :ARG0-of i :ARG0-of (i / insure-02))')
    appears_inverted(g, ('i', ':ARG0', 'c'))
    codec.encode(g)


def test_node_contexts():
    g = codec.decode('(a / alpha)')
    assert node_contexts(g) == ['a']

    # note here and below: the first 'a' is for ('a', ':instance', None)
    g = codec.decode('(a :ARG0 (b / beta))')
    assert node_contexts(g) == ['a', 'a', 'b']

    g = codec.decode('(a :ARG0-of (b / beta))')
    assert node_contexts(g) == ['a', 'a', 'b']

    # also ('b', ':instance', None) here
    g = codec.decode('(a :ARG0 (b) :ARG1 (g / gamma))')
    assert node_contexts(g) == ['a', 'a', 'b', 'a', 'g']


def test_issue_92():
    # https://github.com/goodmami/penman/issues/92
    g = codec.decode('(a / alpha :ARG0~e.0 (b / beta))')
    assert configure(g) == Tree(
        ('a', [('/', 'alpha'),
               (':ARG0~e.0', ('b', [('/', 'beta')]))]))
    assert configure(g, top='b') == Tree(
        ('b', [('/', 'beta'),
               (':ARG0-of~e.0', ('a', [('/', 'alpha')]))]))


def test_issue_93():
    # https://github.com/goodmami/penman/issues/93
    g = codec.decode('(a / alpha :ARG0 b~1)')
    g.triples.append(('b', ':instance', 'beta'))
    assert configure(g) == Tree(
        ('a', [('/', 'alpha'),
               (':ARG0', ('b', [('/', 'beta')]))]))
