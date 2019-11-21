# -*- coding: utf-8 -*-

import pytest

import penman
from penman import layout
from penman import surface

codec = penman.PENMANCodec()
decode = codec.decode
encode = codec.encode


def b(role, tgt, epis=None):
    """
    Make a tree branch with all 3 fields.
    """
    if not epis:
        epis = []
    return (role, tgt, epis)


class TestPENMANCodec(object):
    def test_parse(self):
        assert codec.parse('()') == (
            None, [])
        assert codec.parse('(a)') == (
            'a', [])
        assert codec.parse('(a / )') == (
            'a', [b('/', None)])
        assert codec.parse('(a / alpha)') == (
            'a', [b('/', 'alpha')])
        assert codec.parse('(a : b)') == (
            'a', [b(':', 'b')])
        assert codec.parse('(a : ())') == (
            'a', [b(':', (None, []))])
        assert codec.parse('(a : (b))') == (
            'a', [b(':', ('b', []))])
        assert codec.parse('(a / alpha :ARG (b / beta))') == (
            'a', [b('/', 'alpha'),
                  b(':ARG', ('b', [b('/', 'beta')]))])
        assert codec.parse('(a :ARG-of b)') == (
            'a', [b(':ARG-of', 'b')])
        assert codec.parse('(a :ARG~1 b~2)') == (
            'a', [b(':ARG', 'b', [surface.RoleAlignment((1,)),
                                  surface.Alignment((2,))])])

    def test_format(self):
        assert codec.format(
            (None, [])
        ) == '()'
        assert codec.format(
            ('a', [])
        ) == '(a)'
        assert codec.format(
            ('a', [b('/', None)])
        ) == '(a / )'
        assert codec.format(
            ('a', [b('/', '')])
        ) == '(a / )'
        assert codec.format(
            ('a', [b('/', 'alpha')])
        ) == '(a / alpha)'
        assert codec.format(
            ('a', [b('', 'b')])
        ) == '(a : b)'
        assert codec.format(
            ('a', [b(':', 'b')])
        ) == '(a : b)'
        assert codec.format(
            ('a', [b('', ('b', []))])
        ) == '(a : (b))'
        assert codec.format(
            ('a', [b('/', 'alpha'),
                   b('ARG', ('b', [b('/', 'beta')]))]),
            indent=None
        ) == '(a / alpha :ARG (b / beta))'
        assert codec.format(
            ('a', [b('ARG-of', 'b')])
        ) == '(a :ARG-of b)'
        assert codec.format(
            ('a', [b(':ARG-of', 'b')])
        ) == '(a :ARG-of b)'
        assert codec.format(
            ('a', [b('ARG', 'b', [surface.RoleAlignment((1,)),
                                  surface.Alignment((2,))])])
        ) == '(a :ARG~1 b~2)'

    def test_format_with_parameters(self):
        # no indent
        assert codec.format(
            ('a', [b('/', 'alpha'), b('ARG', ('b', [b('/', 'beta')]))]),
            indent=None
        ) == '(a / alpha :ARG (b / beta))'
        # default (adaptive) indent
        assert codec.format(
            ('a', [b('/', 'alpha'), b('ARG', ('b', [b('/', 'beta')]))]),
            indent=-1
        ) == ('(a / alpha\n'
              '   :ARG (b / beta))')
        # fixed indent
        assert codec.format(
            ('a', [b('/', 'alpha'), b('ARG', ('b', [b('/', 'beta')]))]),
            indent=6
        ) == ('(a / alpha\n'
              '      :ARG (b / beta))')
        # default compactness of attributes
        assert codec.format(
            ('a', [b('/', 'alpha'),
                   b('polarity', '-'),
                   b('ARG', ('b', [b('/', 'beta')]))]),
            compact=False
        ) == ('(a / alpha\n'
              '   :polarity -\n'
              '   :ARG (b / beta))')
        # compact of attributes
        assert codec.format(
            ('a', [b('/', 'alpha'),
                   b('polarity', '-'),
                   b('ARG', ('b', [b('/', 'beta')]))]),
            compact=True
        ) == ('(a / alpha :polarity -\n'
              '   :ARG (b / beta))')
        # compact of attributes (only initial)
        assert codec.format(
            ('a', [b('/', 'alpha'),
                   b('polarity', '-'),
                   b('ARG', ('b', [b('/', 'beta')])),
                   b('mode', 'expressive')]),
            compact=True
        ) == ('(a / alpha :polarity -\n'
              '   :ARG (b / beta)\n'
              '   :mode expressive)')

    def test_decode(self, x1):
        # unlabeled single node
        g = decode('(a)')
        assert g.top == 'a'
        assert g.triples == []

        # labeled node
        g = decode('(a / alpha)')
        assert g.top == 'a'
        assert g.triples == [('a', ':instance', 'alpha')]

        # unlabeled edge to unlabeled node
        g = decode('(a : (b))')
        assert g.top == 'a'
        assert g.triples == [('a', ':', 'b')]

        # inverted unlabeled edge
        g = decode('(b :-of (a))')
        assert g.top == 'b'
        assert g.triples == [('a', ':', 'b')]

        # labeled edge to unlabeled node
        g = decode('(a :ARG (b))')
        assert g.top == 'a'
        assert g.triples == [('a', ':ARG', 'b')]

        # inverted edge
        g = decode('(b :ARG-of (a))')
        assert g.top == 'b'
        assert g.triples == [('a', ':ARG', 'b')]

        # fuller examples
        assert decode(x1[0]).triples == x1[1]

    def test_decode_atoms(self):
        # string value
        g = decode('(a :ARG "string")')
        assert g.triples == [
            ('a', ':ARG', '"string"'),
        ]

        # symbol value
        g = decode('(a :ARG symbol)')
        assert g.triples == [
            ('a', ':ARG', 'symbol')
        ]

        # float value
        g = decode('(a :ARG -1.0e-2)')
        assert g.triples == [
            ('a', ':ARG', -0.01)
        ]

        # int value
        g = decode('(a :ARG 15)')
        assert g.triples == [
            ('a', ':ARG', 15)
        ]

        # numeric concept
        g = decode('(one / 1)')
        assert g.triples == [
            ('one', ':instance', 1)
        ]

        # string concept
        g = decode('(one / "a string")')
        assert g.triples == [
            ('one', ':instance', '"a string"')
        ]

        # numeric symbol (from https://github.com/goodmami/penman/issues/17)
        g = decode('(g / go :null_edge (x20 / 876-9))')
        assert g.triples == [
            ('g', ':instance', 'go'),
            ('g', ':null_edge', 'x20'),
            ('x20', ':instance', '876-9'),
        ]

    def test_decode_invalid_graphs(self):
        # some robustness
        g = decode('(g / )')
        assert g.triples == [
            ('g', ':instance', None)
        ]

        g = decode('(g / :ARG0 (i / i))')
        assert g.triples == [
            ('g', ':instance', None),
            ('g', ':ARG0', 'i'),
            ('i', ':instance', 'i')
        ]

        g = decode('(g / go :ARG0 :ARG1 (t / there))')
        assert g.triples == [
            ('g', ':instance', 'go'),
            ('g', ':ARG0', None),
            ('g', ':ARG1', 't'),
            ('t', ':instance', 'there')
        ]

        # invalid strings
        with pytest.raises(penman.DecodeError):
            decode('(')
        with pytest.raises(penman.DecodeError):
            decode('(a')
        with pytest.raises(penman.DecodeError):
            decode('(a /')
        with pytest.raises(penman.DecodeError):
            decode('(a / alpha')
        with pytest.raises(penman.DecodeError):
            decode('(a b)')
        with pytest.raises(penman.DecodeError):
            decode('(1 / one)')

    def test_encode(self, x1):
        # empty graph
        g = penman.Graph([])
        assert encode(g) == '()'

        # unlabeled single node
        g = penman.Graph([], top='a')
        assert encode(g) == '(a)'

        # labeled node
        g = penman.Graph([('a', ':instance', 'alpha')])
        assert encode(g) == '(a / alpha)'

        # labeled node (without ':')
        g = penman.Graph([('a', 'instance', 'alpha')])
        assert encode(g) == '(a / alpha)'

        # unlabeled edge to unlabeled node
        g = penman.Graph([('a', '', 'b')])
        assert encode(g) == '(a : b)'
        g = penman.Graph([('a', ':', 'b')],
                         epidata={('a', ':', 'b'): [layout.Push('b')]})
        assert encode(g) == '(a : (b))'

        # inverted unlabeled edge
        g = penman.Graph(
            [('a', '', 'b')], top='b')
        assert encode(g) == '(b :-of a)'

        # labeled edge to unlabeled node
        g = penman.Graph([('a', 'ARG', 'b')])
        assert encode(g) == '(a :ARG b)'

        # inverted edge
        g = penman.Graph([('a', 'ARG', 'b')], top='b')
        assert encode(g) == '(b :ARG-of a)'

    def test_encode_atoms(self):
        # string value
        g = penman.Graph([('a', 'ARG', '"string"')])
        assert encode(g) == '(a :ARG "string")'

        # symbol value
        g = penman.Graph([('a', 'ARG', 'symbol')])
        assert encode(g) == '(a :ARG symbol)'

        # float value
        g = penman.Graph([('a', 'ARG', -0.01)])
        assert encode(g) == '(a :ARG -0.01)'

        # int value
        g = penman.Graph([('a', 'ARG', 15)])
        assert encode(g) == '(a :ARG 15)'

        # numeric concept
        g = penman.Graph([('one', 'instance', 1)])
        assert encode(g) == '(one / 1)'

        # string concept
        g = penman.Graph([('one', 'instance', '"a string"')])
        assert encode(g) == '(one / "a string")'
