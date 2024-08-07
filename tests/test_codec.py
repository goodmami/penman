# -*- coding: utf-8 -*-

import logging

import pytest

import penman
from penman import layout
from penman import surface

codec = penman.PENMANCodec()
decode = codec.decode
encode = codec.encode


class TestPENMANCodec(object):
    def test_parse(self):
        assert codec.parse('(a / alpha)') == ('a', [('/', 'alpha')])

    def test_parse_triples(self):
        assert codec.parse_triples('role(a, b)') == [('a', ':role', 'b')]

    def test_format(self):
        assert codec.format(('a', [('/', 'alpha')])) == '(a / alpha)'

    def test_decode(self, x1):
        # unlabeled single node
        g = decode('(a)')
        assert g.top == 'a'
        assert g.triples == [('a', ':instance', None)]

        # labeled node
        g = decode('(a / alpha)')
        assert g.top == 'a'
        assert g.triples == [('a', ':instance', 'alpha')]

        # unlabeled edge to unlabeled node
        g = decode('(a : (b))')
        assert g.top == 'a'
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':', 'b'),
            ('b', ':instance', None),
        ]

        # inverted unlabeled edge
        g = decode('(b :-of (a))')
        assert g.top == 'b'
        assert g.triples == [
            ('b', ':instance', None),
            ('a', ':', 'b'),
            ('a', ':instance', None),
        ]

        # labeled edge to unlabeled node
        g = decode('(a :ARG (b))')
        assert g.top == 'a'
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG', 'b'),
            ('b', ':instance', None),
        ]

        # inverted edge
        g = decode('(b :ARG-of (a))')
        assert g.top == 'b'
        assert g.triples == [
            ('b', ':instance', None),
            ('a', ':ARG', 'b'),
            ('a', ':instance', None),
        ]

        # fuller examples
        assert decode(x1[0]).triples == x1[1]

    def test_decode_inverted_attributes(self, caplog):
        caplog.set_level(logging.WARNING, logger='penman.layout')

        g = decode('(b :-of 1)')
        assert g.top == 'b'
        assert g.triples == [
            ('b', ':instance', None),
            ('b', ':-of', '1'),
        ]
        assert 'cannot deinvert attribute' in caplog.text
        assert g.variables() == {'b'}
        caplog.clear()

        g = decode('(a :ARG-of "string")')
        assert g.top == 'a'
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG-of', '"string"'),
        ]
        assert 'cannot deinvert attribute' in caplog.text
        assert g.variables() == {'a'}
        caplog.clear()

    def test_decode_atoms(self):
        # string value
        g = decode('(a :ARG "string")')
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG', '"string"'),
        ]

        # symbol value
        g = decode('(a :ARG symbol)')
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG', 'symbol')
        ]

        # float value
        g = decode('(a :ARG -1.0e-2)')
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG', '-1.0e-2')
        ]

        # int value
        g = decode('(a :ARG 15)')
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG', '15')
        ]

        # numeric concept
        g = decode('(one / 1)')
        assert g.triples == [
            ('one', ':instance', '1')
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

    def test_decode_alignments(self):
        g = decode('(a / alpha~1)')
        assert g.triples == [
            ('a', ':instance', 'alpha'),
        ]
        assert surface.alignments(g) == {
            ('a', ':instance', 'alpha'): surface.Alignment((1,)),
        }
        assert surface.role_alignments(g) == {}

        assert decode('(a / alpha~1)') == decode('(a / alpha ~1)')

        g = decode('(a :ARG~e.1,2 b)')
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG', 'b'),
        ]
        assert surface.alignments(g) == {}
        assert surface.role_alignments(g) == {
            ('a', ':ARG', 'b'): surface.RoleAlignment((1, 2), prefix='e.'),
        }

        # https://github.com/goodmami/penman/issues/50
        g = decode('(a :ARG1 "str~ing" :ARG2 "str~ing"~1)')
        assert g.triples == [
            ('a', ':instance', None),
            ('a', ':ARG1', '"str~ing"'),
            ('a', ':ARG2', '"str~ing"'),
        ]
        assert surface.alignments(g) == {
            ('a', ':ARG2', '"str~ing"'): surface.Alignment((1,)),
        }
        assert surface.role_alignments(g) == {}

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
        # the following is not a problem while numbers are symbols
        # with pytest.raises(penman.DecodeError):
        #     decode('(1 / one)')

    def test_decode_recursion_limit(self):
        # Create a graph with n levels of nesting. Inefficient
        # recursive-descent parsers will hit a RecursionError and be
        # unable to parse some graphs. n should be some reasonable
        # minimum.
        n = 200
        s = (''.join(f'(a{i} / A :ARG0 ' for i in range(n-1))
             + f'(a{n} / A)'
             + ')' * (n-1))
        g = decode(s)  # hopefully no RecursionError
        assert len(g.triples) == (n         # n :instance triples
                                  + n - 1)  # n - 1 :ARG0 triples

    def test_decode_issue_143(self):
        # https://github.com/goodmami/penman/issues/143
        with pytest.raises(penman.DecodeError):
            decode('(a :op ")')
        with pytest.raises(penman.DecodeError):
            decode('(a :op1 " :op2 "foo")')
        with pytest.raises(penman.DecodeError):
            decode('(a :" foo)')


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

    def test_encode_issue_61(self):
        # https://github.com/goodmami/penman/issues/61
        g = penman.Graph([('i2', ':instance', 'i'),
                          ('i', ':instance', 'i'),
                          ('i2', ':ARG0', 'i')],
                         top='i2')
        assert encode(g, indent=None) == '(i2 / i :ARG0 (i / i))'

    def test_encode_issue_67(self):
        # https://github.com/goodmami/penman/issues/61
        triples = [('h', ':instance', 'have-org-role-91'),
                   ('a', ':instance', 'activist'),
                   ('h', ':ARG0', 'a'),
                   ('h', ':ARG2', 'a')]
        assert encode(penman.Graph(triples, top='a')) == (
            '(a / activist\n'
            '   :ARG0-of (h / have-org-role-91)\n'
            '   :ARG2-of h)')
        assert encode(penman.Graph(triples, top='h')) == (
            '(h / have-org-role-91\n'
            '   :ARG0 (a / activist)\n'
            '   :ARG2 a)')
