# -*- coding: utf-8 -*-

import pytest

import penman

codec = penman.PENMANCodec()
decode = codec.decode
encode = penman.encode

class TestPENMANCodec(object):
    def test_decode(self, x1, x2):
        # unlabeled single node
        g = decode('(a)')
        assert g.triples() == [('a', 'instance', None)]

        # labeled node
        g = decode('(a / alpha)')
        assert g.triples() == [('a', 'instance', 'alpha')]

        # unlabeled edge to unlabeled node
        g = decode('(a : (b))')
        assert g.triples() == [
            ('a', 'instance', None),
            ('a', '', 'b'),
            ('b', 'instance', None),
        ]
        assert g.top == 'a'

        # inverted unlabeled edge
        g = decode('(b :-of (a))')
        assert g.triples() == [
            ('b', 'instance', None),
            ('a', '', 'b'),
            ('a', 'instance', None),
        ]
        assert g.top == 'b'

        # labeled edge to unlabeled node
        g = decode('(a :ARG (b))')
        assert g.triples() == [
            ('a', 'instance', None),
            ('a', 'ARG', 'b'),
            ('b', 'instance', None),
        ]
        assert g.top == 'a'

        # inverted edge
        g = decode('(b :ARG-of (a))')
        assert g.triples() == [
            ('b', 'instance', None),
            ('a', 'ARG', 'b'),
            ('a', 'instance', None),
        ]
        assert g.top == 'b'

        # fuller examples
        assert decode(x1[0]).triples() == x1[1]
        assert decode(x2[0]).triples() == x2[1]

    def test_decode_atoms(self):
        # string value
        g = decode('(a :ARG "string")')
        assert g.triples() == [
            ('a', 'instance', None),
            ('a', 'ARG', '"string"'),
        ]

        # symbol value
        g = decode('(a :ARG symbol)')
        assert g.triples() == [
            ('a', 'instance', None),
            ('a', 'ARG', 'symbol')
        ]

        # float value
        g = decode('(a :ARG -1.0e-2)')
        assert g.triples() == [
            ('a', 'instance', None),
            ('a', 'ARG', -0.01)
        ]

        # int value
        g = decode('(a :ARG 15)')
        assert g.triples() == [
            ('a', 'instance', None),
            ('a', 'ARG', 15)
        ]

        # numeric node type
        g = decode('(one / 1)')
        assert g.triples() == [
            ('one', 'instance', 1)
        ]

        # string node type
        g = decode('(one / "a string")')
        assert g.triples() == [
            ('one', 'instance', '"a string"')
        ]

        # numeric "variable"
        g = decode('(1 / one)')
        assert g.triples() == [
            (1, 'instance', 'one')
        ]

        # numeric symbol (from https://github.com/goodmami/penman/issues/17)
        g = decode('(g / go :null_edge (x20 / 876-9))')
        assert g.triples() == [
            ('g', 'instance', 'go'),
            ('g', 'null_edge', 'x20'),
            ('x20', 'instance', '876-9'),
        ]

    def test_decode_invalid_graphs(self):
        # some robustness
        g = decode('(g / )')
        assert g.triples() == [
            ('g', 'instance', None)
        ]

        g = decode('(g / :ARG0 (i / i))')
        assert g.triples() == [
            ('g', 'instance', None),
            ('g', 'ARG0', 'i'),
            ('i', 'instance', 'i')
        ]

        g = decode('(g / go :ARG0 :ARG1 (t / there))')
        assert g.triples() == [
            ('g', 'instance', 'go'),
            ('g', 'ARG0', None),
            ('g', 'ARG1', 't'),
            ('t', 'instance', 'there')
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
            decode('()')
        with pytest.raises(penman.DecodeError):
            decode('(a :ARG1 ())')


# def test_iterdecode():
#     codec = penman.PENMANCodec()
#     assert len(list(codec.iterdecode('(h / hello)(g / goodbye)'))) == 2
#     assert len(list(codec.iterdecode(
#         '# comment (n / not :ARG (g / graph))\n'
#         '(g / graph\n'
#         '   :quant 1)\n'
#         'some text, then (g / graph :quant (a / another))'))) == 2
#     # uncomment below if not reraising exceptions in iterdecode
#     # assert len(list(codec.iterdecode('(h / hello'))) == 0
#     # assert len(list(codec.iterdecode('(h / hello)(g / goodbye'))) == 1


    # def test_encode(self, x1, x2):
    #     # unlabeled single node
    #     g = penman.Graph([('a', 'instance', None)])
    #     assert encode(g) == '(a)'

    #     # labeled node
    #     g = penman.Graph([('a', 'instance', 'alpha')])
    #     assert encode(g) == '(a / alpha)'

    #     # unlabeled edge to unlabeled node
    #     g = penman.Graph([
    #         ('a', 'instance', None),
    #         ('a', None, 'b'),
    #         ('b', 'instance', None),
    #     ])
    #     assert encode(g) == '(a : (b))'

    #     # inverted unlabeled edge
    #     g = penman.Graph([
    #         ('b', 'instance', None),
    #         ('a', None, 'b'),
    #         ('a', 'instance', None),
    #     ])
    #     assert encode(g) == '(b :-of (a))'

    #     # labeled edge to unlabeled node
    #     g = penman.Graph([
    #         ('a', 'instance', None),
    #         ('a', 'ARG', 'b'),
    #         ('b', 'instance', None),
    #     ])
    #     assert encode(g) == '(a :ARG (b))'

    #     # inverted edge
    #     g = penman.Graph([
    #         ('b', 'instance', None),
    #         ('a', 'ARG', 'b'),
    #         ('a', 'instance', None),
    #     ])
    #     assert encode(g) == '(b :ARG-of (a))'

    # def test_encode_atoms(self):
    #     # string value
    #     g = penman.Graph([
    #         ('a', 'instance', None),
    #         ('a', 'ARG', '"string"'),
    #     ])
    #     assert encode(g) == '(a :ARG "string")'

    #     # symbol value
    #     g = penman.Graph([
    #         ('a', 'instance', None),
    #         ('a', 'ARG', 'symbol'),
    #     ])
    #     assert encode(g) == '(a :ARG symbol)'

    #     # float value
    #     g = penman.Graph([
    #         ('a', 'instance', None),
    #         ('a', 'ARG', -0.01),
    #     ])
    #     assert encode(g) == '(a :ARG -0.01)'

    #     # int value
    #     g = penman.Graph([
    #         ('a', 'instance', None),
    #         ('a', 'ARG', 15),
    #     ])
    #     assert encode(g) == '(a :ARG 15)'

    #     # numeric node type
    #     g = penman.Graph([
    #         ('one', 'instance', 1),
    #     ])
    #     assert encode(g) == '(one / 1)'

    #     # string node type
    #     g = penman.Graph([
    #         ('one', 'instance', '"a string"'),
    #     ])
    #     assert encode(g) == '(one / "a string")'

    #     # numeric "variable"
    #     g = penman.Graph([
    #         (1, 'instance', 'one'),
    #     ])
    #     assert encode(g) == '(1 / one)'


#     assert encode(penman.Graph(x1[1])) == x1[0]
#     assert encode(penman.Graph(x2[1])) == x2[0]

#     # reentrancy under inversion
#     g = penman.Graph([
#         ('a', 'instance', 'aaa'),
#         ('b', 'instance', 'bbb'),
#         ('c', 'instance', 'ccc'),
#         ('b2', 'instance', 'bbb'),
#         ('a', 'ARG1', 'b'),
#         ('c', 'ARG1', 'b2'),
#         ('c', 'ARG2', 'a')
#     ])
#     assert encode(g) == (
#         '(a / aaa\n'
#         '   :ARG1 (b / bbb)\n'
#         '   :ARG2-of (c / ccc\n'
#         '               :ARG1 (b2 / bbb)))'
#     )

#     # custom codec
#     class TestCodec(penman.PENMANCodec):
#         TYPE_REL = 'test'

#     g = penman.Graph([
#         ('a', 'test', 'alpha')
#     ])
#     assert encode(g, cls=TestCodec) == '(a / alpha)'

#     # empty graph
#     g = penman.Graph()
#     with pytest.raises(penman.EncodeError):
#         encode(g)

#     # disconnected graph
#     g = penman.Graph([
#         ('a', 'instance', 'alpha'),
#         ('b', 'instance', 'beta')
#     ])
#     with pytest.raises(penman.EncodeError):
#         encode(g)


# def test_encode_with_parameters():
#     encode = penman.encode
#     g = penman.Graph([
#         ('a', 'instance', 'aaa'),
#         ('b', 'instance', 'bbb'),
#         ('c', 'instance', 'ccc'),
#         ('a', 'ARG1', 'b'),
#         ('b', 'ARG1', 'c')
#     ])
#     assert encode(g, indent=True) == (
#         '(a / aaa\n'
#         '   :ARG1 (b / bbb\n'
#         '            :ARG1 (c / ccc)))'
#     )
#     assert encode(g, indent=False) == (
#         '(a / aaa :ARG1 (b / bbb :ARG1 (c / ccc)))'
#     )
#     assert encode(g, indent=None) == (
#         '(a / aaa :ARG1 (b / bbb :ARG1 (c / ccc)))'
#     )
#     assert encode(g, indent=0) == (
#         '(a / aaa\n'
#         ':ARG1 (b / bbb\n'
#         ':ARG1 (c / ccc)))'
#     )
#     assert encode(g, indent=2) == (
#         '(a / aaa\n'
#         '  :ARG1 (b / bbb\n'
#         '    :ARG1 (c / ccc)))'
#     )
#     assert encode(g, top='b') == (
#         '(b / bbb\n'
#         '   :ARG1 (c / ccc)\n'
#         '   :ARG1-of (a / aaa))'
#     )
#     assert encode(g, top='c') == (
#         '(c / ccc\n'
#         '   :ARG1-of (b / bbb\n'
#         '               :ARG1-of (a / aaa)))'
#     )
#     g = penman.decode('(a / aaa~e.1 :ARG0-of (b / bbb~e.2))')
#     assert encode(g, top='b') == (
#         '(b / bbb~e.2\n'
#         '   :ARG0 (a / aaa~e.1))'
#     )
#     g = penman.decode(
#         '(a / aaa~e.1\n'
#         '   :ARG0 (b / bbb~e.2\n'
#         '            :ARG0 c~e.3)\n'
#         '   :ARG1 (c / ccc~e.4))')
#     assert encode(g, top='c') == (
#         '(c / ccc~e.4\n'
#         '   :ARG0-of (b / bbb~e.2)\n'
#         '   :ARG1-of (a / aaa~e.1\n'
#         '               :ARG0 b))'
#     )


# def test_loads():
#     assert penman.loads('') == []
#     assert penman.loads('# comment') == []
#     assert penman.loads('# comment (n / not :ARG (g / graph))') == []
#     assert len(penman.loads('(a / aaa)')) == 1
#     assert len(penman.loads('(a / aaa)\n(b / bbb)')) == 2
#     assert len(penman.loads(
#         '# comment\n'
#         '(a / aaa\n'
#         '   :ARG1 (b / bbb))\n'
#         '\n'
#         '# another comment\n'
#         '(b / bbb)\n'
#     )) == 2


# def test_loads_triples():
#     assert penman.loads('', triples=True) == []
#     assert len(penman.loads('instance(a, alpha)', triples=True)) == 1
#     assert len(penman.loads('string(a, "alpha")', triples=True)) == 1

#     gs = penman.loads('instance(a, alpha)ARG(a, b)', triples=True)
#     assert len(gs) == 2
#     assert gs[0].triples() == [('a', 'instance', 'alpha')]
#     assert gs[1].triples() == [('a', 'ARG', 'b')]

#     gs = penman.loads('instance(a, alpha)^ARG(a, b)', triples=True)
#     assert len(gs) == 1
#     assert gs[0].triples() == [('a', 'instance', 'alpha'), ('a', 'ARG', 'b')]

#     gs = penman.loads('instance(1, alpha)', triples=True)
#     assert gs[0].triples() == [(1, 'instance', 'alpha')]

#     gs = penman.loads('instance(1.1, alpha)', triples=True)
#     assert gs[0].triples() == [(1.1, 'instance', 'alpha')]

#     gs = penman.loads('instance("a string", alpha)', triples=True)
#     assert gs[0].triples() == [('"a string"', 'instance', 'alpha')]

#     class TestCodec(penman.PENMANCodec):
#         TYPE_REL = 'test'
#         TOP_VAR = 'TOP'
#         TOP_REL = 'top'
#     gs = penman.loads(
#         'test(a, alpha)^test(b, beta)^ARG(a, b)^top(TOP, b)',
#         triples=True, cls=TestCodec
#     )
#     assert len(gs) == 1
#     assert gs[0].triples() == [
#         ('a', 'test', 'alpha'),
#         ('b', 'test', 'beta'),
#         ('a', 'ARG', 'b')
#     ]
#     assert gs[0].top == 'b'

#     gs = penman.loads(
#         'test(a, alpha)^test(b, beta)^ARG(a, b)',
#         triples=True, cls=TestCodec
#     )
#     assert gs[0].top == 'a'


# def test_dumps():
#     assert penman.dumps([]) == ''
#     assert penman.dumps([penman.Graph([('a', 'instance', None)])]) == '(a)'
#     assert penman.dumps([
#         penman.Graph([('a', 'instance', None)]),
#         penman.Graph([('b', 'instance', None)]),
#     ]) == '(a)\n\n(b)'


# def test_dumps_triples():
#     assert penman.dumps(
#         [penman.Graph([('a', 'instance', None)])], triples=True
#     ) == 'instance(a, None)'
#     assert penman.dumps(
#         [penman.Graph([('a', 'instance', 'aaa')])], triples=True
#     ) == 'instance(a, aaa)'
#     assert penman.dumps(
#         [penman.Graph([('a', 'instance', None), ('a', 'ARG', 'b')])],
#         triples=True
#     ) == 'instance(a, None) ^\nARG(a, b)'

#     assert penman.dumps(
#         [penman.Graph([(1, 'instance', 'alpha')])],
#         triples=True
#     ) == 'instance(1, alpha)'

#     assert penman.dumps(
#         [penman.Graph([(1.1, 'instance', 'alpha')])],
#         triples=True
#     ) == 'instance(1.1, alpha)'

#     assert penman.dumps(
#         [penman.Graph([('"a string"', 'instance', 'alpha')])],
#         triples=True
#     ) == 'instance("a string", alpha)'

#     class TestCodec(penman.PENMANCodec):
#         TYPE_REL = 'test'
#         TOP_VAR = 'TOP'
#         TOP_REL = 'top'
#     assert penman.dumps(
#         [penman.Graph([('a', 'ARG', 'b')])],
#         triples=True, cls=TestCodec
#     ) == 'top(TOP, a) ^\nARG(a, b)'


# def test_AMRCodec():
#     c = penman.AMRCodec()

#     assert c.invert_relation('ARG0') == 'ARG0-of'
#     assert c.invert_relation('ARG0-of') == 'ARG0'
#     assert c.invert_relation('domain') == 'mod'
#     assert c.invert_relation('mod') == 'domain'
#     assert c.invert_relation('consist-of') == 'consist-of-of'
#     assert c.invert_relation('consist-of-of') == 'consist-of'

#     with pytest.raises(penman.PenmanError):
#         c.invert_relation('instance')

#     assert c.encode(penman.Graph([
#         ('w', 'instance', 'want-01'), ('w', 'ARG0', 'b'), ('w', 'ARG1', 'g'),
#         ('b', 'instance', 'boy'), ('g', 'instance', 'go'), ('g', 'ARG0', 'b')
#     ])) == (
#         '(w / want-01\n'
#         '   :ARG0 (b / boy)\n'
#         '   :ARG1 (g / go\n'
#         '            :ARG0 b))'
#     )

#     g = penman.Graph([('g', 'instance', 'gold'), ('g', 'consist-of-of', 'r'),
#                       ('r', 'instance', 'ring')])
#     assert c.encode(g) == (
#         '(g / gold\n'
#         '   :consist-of-of (r / ring))'
#     )
#     assert c.encode(g, top='r') == (
#         '(r / ring\n'
#         '   :consist-of (g / gold))'
#     )

#     g = penman.Graph([('w', 'instance', 'white'), ('w', 'domain', 'c'),
#                       ('c', 'instance', 'cat')])
#     assert c.encode(g) == (
#         '(w / white\n'
#         '   :domain (c / cat))'
#     )
#     assert c.encode(g, top='c') == (
#         '(c / cat\n'
#         '   :mod (w / white))'
#     )

#     assert c.decode('(g / go)').triples() == [('g', 'instance', 'go')]
#     # example adapted from https://github.com/goodmami/penman/issues/17
#     assert c.decode('(g / go :null_edge (x20 / 876-9))').triples() == [
#         ('g', 'instance', 'go'),
#         ('x20', 'instance', '876-9'),
#         ('g', 'null_edge', 'x20')
#     ]

#     with pytest.raises(penman.DecodeError):
#         c.decode('(g)')  # no concept or relations
#     with pytest.raises(penman.DecodeError):
#         c.decode('(g :ARG0 b)')  # no concept
#     with pytest.raises(penman.DecodeError):
#         c.decode('(g :ARG0 (b / boy) / go)')  # concept after relations
#     with pytest.raises(penman.DecodeError):
#         c.decode('(1 / one)')  # bad variable form
#     with pytest.raises(penman.DecodeError):
#         c.decode('(g / go : (b / boy))')  # anonymous relation

#     # "ISI-style" alignments
#     # ::tok The cat was chased by the dog .
#     g = c.decode(
#         '(c / chase-01~e.3 :ARG0~e.4 (d / dog~e.6) :ARG1 (c2 / cat~e.1))'
#     )
#     assert g.triples() == [
#         ('c', 'instance', 'chase-01'),
#         ('d', 'instance', 'dog'),
#         ('c2', 'instance', 'cat'),
#         ('c', 'ARG0', 'd'),
#         ('c', 'ARG1', 'c2')
#     ]
#     assert g.alignments() == {
#         ('c', 'instance', 'chase-01'): [3],
#         ('d', 'instance', 'dog'): [6],
#         ('c2', 'instance', 'cat'): [1]
#     }
#     assert g.role_alignments() == {
#         ('c', 'ARG0', 'd'): [4]
#     }
#     assert c.encode(g) == (
#         '(c / chase-01~e.3\n'
#         '   :ARG0~e.4 (d / dog~e.6)\n'
#         '   :ARG1 (c2 / cat~e.1))'
#     )

