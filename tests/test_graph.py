# -*- coding: utf-8 -*-

import pytest

import penman


class TestGraph(object):
    def test_init(self):
        # empty graph
        with pytest.raises(TypeError):
            g = penman.Graph()

        # single node
        g = penman.Graph([('a', 'instance', None)])
        assert g.triples() == [('a', 'instance', None)]
        assert g.top == 'a'

        # single node one edge (default nodetype)
        g = penman.Graph([('a', 'ARG1', 'b')])
        assert g.triples() == [('a', 'ARG1', 'b')]
        assert g.top == 'a'

        # first triple determines top
        g = penman.Graph([('b', 'instance', None), ('a', 'ARG1', 'b')])
        assert g.triples() == [
            ('b', 'instance', None),
            ('a', 'ARG1', 'b')
        ]
        assert g.top == 'b'

    def test_top(self, x1):
        assert penman.Graph([('a', 'instance', None)]).top == 'a'
        assert penman.Graph(
            [('b', 'instance', None), ('a', 'ARG', 'b')]
        ).top == 'b'
        assert penman.Graph(x1[1]).top == 'e2'

    def test_variables(self, x1):
        assert penman.Graph([('a', 'ARG', 'b')]).variables() == set(['a'])
        assert penman.Graph(x1[1]).variables() == set(['e2', 'x1', '_1', 'e3'])

    def test_triples(self, x1):
        g = penman.Graph(x1[1])
        assert g.triples() == [
            ('e2', 'instance', '_try_v_1'),
            ('e2', 'ARG1', 'x1'),
            ('x1', 'instance', 'named'),
            ('x1', 'CARG', '"Abrams"'),
            ('_1', 'RSTR', 'x1'),
            ('_1', 'instance', 'proper_q'),
            ('e2', 'ARG2', 'e3'),
            ('e3', 'instance', '_sleep_v_1'),
            ('e3', 'ARG1', 'x1'),
        ]
        assert g.triples(source='e2') == [
            ('e2', 'instance', '_try_v_1'),
            ('e2', 'ARG1', 'x1'),
            ('e2', 'ARG2', 'e3'),
        ]
        assert g.triples(target='x1') == [
            ('e2', 'ARG1', 'x1'),
            ('_1', 'RSTR', 'x1'),
            ('e3', 'ARG1', 'x1'),
        ]
        assert g.triples(role='instance') == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
        ]

    def test_edges(self, x1):
        g = penman.Graph(x1[1])
        assert g.edges() == [
            ('e2', 'ARG1', 'x1'),
            ('_1', 'RSTR', 'x1'),
            ('e2', 'ARG2', 'e3'),
            ('e3', 'ARG1', 'x1'),
        ]
        assert g.edges(source='e2') == [
            ('e2', 'ARG1', 'x1'),
            ('e2', 'ARG2', 'e3'),
        ]
        assert g.edges(source='e3') == [
            ('e3', 'ARG1', 'x1')
        ]
        assert g.edges(target='e3') == [
            ('e2', 'ARG2', 'e3')
        ]
        assert g.edges(role='RSTR') == [
            ('_1', 'RSTR', 'x1')
        ]

    def test_attributes(self, x1):
        g = penman.Graph(x1[1])
        assert g.attributes() == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('x1', 'CARG', '"Abrams"'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
        ]
        assert g.attributes(source='x1') == [
            ('x1', 'instance', 'named'),
            ('x1', 'CARG', '"Abrams"'),
        ]
        assert g.attributes(target='named') == [
            ('x1', 'instance', 'named'),
        ]
        assert g.attributes(role='instance') == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
        ]

    def test_reentrancies(self, x1):
        g = penman.Graph(x1[1])
        assert g.reentrancies() == {'x1': 2}
        # top has an implicit entrancy
        g = penman.Graph([
            ('b', 'instance', 'bark'),
            ('b', 'ARG1', 'd'),
            ('d', 'instance', 'dog'),
            ('w', 'ARG1', 'b'),
            ('w', 'instance', 'wild'),
        ])
        assert g.reentrancies() == {'b': 1}
