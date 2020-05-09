# -*- coding: utf-8 -*-

import penman

Graph = penman.Graph


class TestGraph(object):
    def test_init(self):
        # empty graph
        g = Graph()
        assert g.triples == []
        assert g.top is None

        # single node
        g = Graph([('a', 'instance', None)])
        assert g.triples == [('a', ':instance', None)]
        assert g.top == 'a'

        # single node one edge (default concept)
        g = Graph([('a', 'ARG1', 'b')])
        assert g.triples == [('a', ':ARG1', 'b')]
        assert g.top == 'a'

        # first triple determines top
        g = Graph([('b', ':instance', None), ('a', ':ARG1', 'b')])
        assert g.triples == [
            ('b', ':instance', None),
            ('a', ':ARG1', 'b')
        ]
        assert g.top == 'b'

    def test__or__(self):
        p = Graph()
        g = p | p
        assert g.triples == []
        assert g.top is None
        assert g is not p

        q = Graph([('a', ':instance', 'alpha')])
        g = p | q
        assert g.triples == [('a', ':instance', 'alpha')]
        assert g.top == 'a'
        assert g is not q is not p  # noqa: E714  <-- pycodestyle bug fixed upstream

        r = Graph([('a', ':ARG', 'b'), ('b', ':instance', 'beta')], top='b')
        g = q | r
        assert g.triples == [('a', ':instance', 'alpha'),
                             ('a', ':ARG', 'b'),
                             ('b', ':instance', 'beta')]
        assert g.top == 'a'

    def test__ior__(self):
        g = Graph()
        original = g
        g |= Graph()
        assert g.triples == []
        assert g.top is None
        assert g is original

        p = Graph([('a', ':instance', 'alpha')])
        g |= p
        assert g.triples == [('a', ':instance', 'alpha')]
        assert g.top == 'a'
        assert g is original

    def test__sub__(self):
        p = Graph()
        g = p - p
        assert g.triples == []
        assert g.top is None
        assert g is not p

        q = Graph([('a', ':instance', 'alpha')])
        g = q - p
        assert g.triples == [('a', ':instance', 'alpha')]
        assert g.top == 'a'
        assert g is not q is not p  # noqa: E714  <-- pycodestyle bug fixed upstream

        g = p - q
        assert g.triples == []
        assert g.top is None

        g = q - q
        assert g.triples == []
        assert g.top is None

    def test__isub__(self):
        g = Graph()
        original = g
        g -= Graph()
        assert g.triples == []
        assert g.top is None
        assert g is original

        g = Graph([('a', ':instance', 'alpha'),
                   ('a', ':ARG', 'b'),
                   ('b', ':instance', 'beta')])
        original = g
        g -= Graph([('a', ':instance', 'alpha'), ('a', ':ARG', 'b')])
        assert g.triples == [('b', ':instance', 'beta')]
        assert g.top == 'b'
        assert g is original

    def test_top(self, x1):
        assert Graph([('a', ':instance', None)]).top == 'a'
        assert Graph(
            [('b', ':instance', None), ('a', ':ARG', 'b')]
        ).top == 'b'
        assert Graph(x1[1]).top == 'e2'

    def test_variables(self, x1):
        assert Graph([('a', ':ARG', 'b')]).variables() == set('a')
        assert Graph(x1[1]).variables() == set(['e2', 'x1', '_1', 'e3'])
        assert Graph([('a', ':ARG', 'b')], top='b').variables() == set('ab')

    def test_instances(self, x1):
        g = Graph(x1[1])
        assert g.instances() == [
            ('e2', ':instance', '_try_v_1'),
            ('x1', ':instance', 'named'),
            ('_1', ':instance', 'proper_q'),
            ('e3', ':instance', '_sleep_v_1'),
        ]

    def test_edges(self, x1):
        g = Graph(x1[1])
        assert g.edges() == [
            ('e2', ':ARG1', 'x1'),
            ('_1', ':RSTR', 'x1'),
            ('e2', ':ARG2', 'e3'),
            ('e3', ':ARG1', 'x1'),
        ]
        assert g.edges(source='e2') == [
            ('e2', ':ARG1', 'x1'),
            ('e2', ':ARG2', 'e3'),
        ]
        assert g.edges(source='e3') == [
            ('e3', ':ARG1', 'x1')
        ]
        assert g.edges(target='e3') == [
            ('e2', ':ARG2', 'e3')
        ]
        assert g.edges(role=':RSTR') == [
            ('_1', ':RSTR', 'x1')
        ]

    def test_edges_issue_81(self, x1):
        g = Graph([('s', ':instance', 'sleep-01'),
                   ('s', ':ARG0', 'i'),
                   ('i', ':instance', 'i')])
        assert g.edges() == [
            ('s', ':ARG0', 'i')
        ]
        assert g.instances() == [
            ('s', ':instance', 'sleep-01'),
            ('i', ':instance', 'i')
        ]

    def test_attributes(self, x1):
        g = Graph(x1[1])
        assert g.attributes() == [
            ('x1', ':CARG', '"Abrams"'),
        ]
        assert g.attributes(source='x1') == [
            ('x1', ':CARG', '"Abrams"'),
        ]
        assert g.attributes(target='"Abrams"') == [
            ('x1', ':CARG', '"Abrams"'),
        ]
        assert g.attributes(role=':instance') == []

    def test_attributes_issue_29(self):
        # https://github.com/goodmami/penman/issues/29
        #
        # added :polarity triple to distinguish instances() from
        # attributes()
        g = Graph([('f', ':instance', 'follow'),
                   ('f', ':polarity', '-'),
                   ('f', ':ARG0', 'i'),
                   ('i', ':instance', 'it'),
                   ('f', ':ARG1', 'i2'),
                   ('i2', ':instance', 'i')])
        assert g.instances() == [
            ('f', ':instance', 'follow'),
            ('i', ':instance', 'it'),
            ('i2', ':instance', 'i'),
        ]
        assert g.attributes() == [
            ('f', ':polarity', '-'),
        ]

    def test_reentrancies(self, x1):
        g = Graph(x1[1])
        assert g.reentrancies() == {'x1': 2}
        # top has an implicit entrancy
        g = Graph([
            ('b', ':instance', 'bark'),
            ('b', ':ARG1', 'd'),
            ('d', ':instance', 'dog'),
            ('w', ':ARG1', 'b'),
            ('w', ':instance', 'wild'),
        ])
        assert g.reentrancies() == {'b': 1}
