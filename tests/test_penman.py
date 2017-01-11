
import pytest

import penman

@pytest.fixture
def x1():
    return (
        '(e2 / _try_v_1\n'
        '    :ARG1 (x1 / named\n'
        '              :CARG "Abrams"\n'
        '              :RSTR-of (_1 / proper_q))\n'
        '    :ARG2 (e3 / _sleep_v_1\n'
        '              :ARG1 x1))',
        [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
            ('e2', 'ARG1', 'x1'),
            ('x1', 'CARG', '"Abrams"'),
            ('_1', 'RSTR', 'x1'),
            ('e2', 'ARG2', 'e3'),
            ('e3', 'ARG1', 'x1'),            
        ]
    )


def test_decode(x1):
    decode = penman.decode

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
        ('b', 'instance', None),
        ('a', None, 'b')
    ]
    assert g.top == 'a'

    # inverted unlabeled edge
    g = decode('(b :-of (a))')
    assert g.triples() == [
        ('b', 'instance', None),
        ('a', 'instance', None),
        ('a', None, 'b')
    ]
    assert g.top == 'b'

    # labeled edge to unlabeled node
    g = decode('(a :ARG (b))')
    assert g.triples() == [
        ('a', 'instance', None),
        ('b', 'instance', None),
        ('a', 'ARG', 'b')
    ]
    assert g.top == 'a'

    # inverted edge
    g = decode('(b :ARG-of (a))')
    assert g.triples() == [
        ('b', 'instance', None),
        ('a', 'instance', None),
        ('a', 'ARG', 'b')
    ]
    assert g.top == 'b'

    # string value
    g = decode('(a :ARG "string")')
    assert g.triples() == [
        ('a', 'instance', None),
        ('a', 'ARG', '"string"')
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

    # fuller example
    assert decode(x1[0]).triples() == x1[1]

    # invalid strings
    with pytest.raises(penman.DecodeError):
        decode('(')
        decode('(a')
        decode('(a /')
        decode('(a / alpha')
        decode('(a b)')

    # custom codec
    class TestCodec(penman.PENMANCodec):
        TYPE_REL = 'test'

    g = decode('(a / alpha)', cls=TestCodec)
    assert g.triples() == [
        ('a', 'test', 'alpha')
    ]
    assert g.top == 'a'
    
def test_decode_triples():
    pass

def test_iterdecode():
    codec = penman.PENMANCodec()
    assert len(list(codec.iterdecode('(h / hello)(g / goodbye)'))) == 2
    assert len(list(codec.iterdecode(
        '# comment (n / not :ARG (g / graph))\n'
        '(g / graph\n'
        '   :quant 1)\n'
        'some text, then (g / graph :quant (a / another))'))) == 2
    # uncomment below if not reraising exceptions in iterdecode
    # assert len(list(codec.iterdecode('(h / hello'))) == 0
    # assert len(list(codec.iterdecode('(h / hello)(g / goodbye'))) == 1

def test_encode(x1):
    encode = penman.encode

    # unlabeled single node
    g = penman.Graph([('a', 'instance', None)])
    assert encode(g) == '(a)'

    # labeled node
    g = penman.Graph([('a', 'instance', 'alpha')])
    assert encode(g) == '(a / alpha)'

    # unlabeled edge to unlabeled node
    g = penman.Graph([
        ('a', 'instance', None),
        ('b', 'instance', None),
        ('a', None, 'b')
    ])
    assert encode(g) == '(a : (b))'

    # inverted unlabeled edge
    g = penman.Graph([
        ('b', 'instance', None),
        ('a', 'instance', None),
        ('a', None, 'b')
    ])
    assert encode(g) == '(b :-of (a))'

    # labeled edge to unlabeled node
    g = penman.Graph([
        ('a', 'instance', None),
        ('b', 'instance', None),
        ('a', 'ARG', 'b')
    ])
    assert encode(g) == '(a :ARG (b))'

    # inverted edge
    g = penman.Graph([
        ('b', 'instance', None),
        ('a', 'instance', None),
        ('a', 'ARG', 'b')
    ])
    assert encode(g) == '(b :ARG-of (a))'

    # string value
    g = penman.Graph([
        ('a', 'instance', None),
        ('a', 'ARG', '"string"')
    ])
    assert encode(g) == '(a :ARG "string")'

    # symbol value
    g = penman.Graph([
        ('a', 'instance', None),
        ('a', 'ARG', 'symbol')
    ])
    assert encode(g) == '(a :ARG symbol)'

    # float value
    g = penman.Graph([
        ('a', 'instance', None),
        ('a', 'ARG', -0.01)
    ])
    assert encode(g) == '(a :ARG -0.01)'

    # int value
    g = penman.Graph([
        ('a', 'instance', None),
        ('a', 'ARG', 15)
    ])
    assert encode(g) == '(a :ARG 15)'

    assert encode(penman.Graph(x1[1])) == x1[0]

    # reentrancy under inversion
    g = penman.Graph([
        ('a', 'instance', 'aaa'),
        ('b', 'instance', 'bbb'),
        ('c', 'instance', 'ccc'),
        ('b2', 'instance', 'bbb'),
        ('a', 'ARG1', 'b'),
        ('c', 'ARG1', 'b2'),
        ('c', 'ARG2', 'a')
    ])
    assert encode(g) == (
        '(a / aaa\n'
        '   :ARG1 (b / bbb)\n'
        '   :ARG2-of (c / ccc\n'
        '               :ARG1 (b2 / bbb)))'
    )

    # custom codec
    class TestCodec(penman.PENMANCodec):
        TYPE_REL = 'test'

    g = penman.Graph([
        ('a', 'test', 'alpha')
    ])
    assert encode(g, cls=TestCodec) == '(a / alpha)'

def test_encode_with_parameters():
    encode = penman.encode
    g = penman.Graph([
        ('a', 'instance', 'aaa'),
        ('b', 'instance', 'bbb'),
        ('c', 'instance', 'ccc'),
        ('a', 'ARG1', 'b'),
        ('b', 'ARG1', 'c')
    ])
    assert encode(g, indent=True) == (
        '(a / aaa\n'
        '   :ARG1 (b / bbb\n'
        '            :ARG1 (c / ccc)))'
    )
    assert encode(g, indent=False) == (
        '(a / aaa :ARG1 (b / bbb :ARG1 (c / ccc)))'
    )
    assert encode(g, indent=None) == (
        '(a / aaa :ARG1 (b / bbb :ARG1 (c / ccc)))'
    )
    assert encode(g, indent=0) == (
        '(a / aaa\n'
        ':ARG1 (b / bbb\n'
        ':ARG1 (c / ccc)))'
    )
    assert encode(g, indent=2) == (
        '(a / aaa\n'
        '  :ARG1 (b / bbb\n'
        '    :ARG1 (c / ccc)))'
    )
    assert encode(g, top='b') == (
        '(b / bbb\n'
        '   :ARG1 (c / ccc)\n'
        '   :ARG1-of (a / aaa))'
    )
    assert encode(g, top='c') == (
        '(c / ccc\n'
        '   :ARG1-of (b / bbb\n'
        '               :ARG1-of (a / aaa)))'
    )

class TestGraph(object):
    def test_init(self):
        # empty graph
        g = penman.Graph()
        assert g.triples() == []
        assert g.top is None

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
        assert penman.Graph().top is None
        assert penman.Graph([('a', 'instance', None)]).top == 'a'
        assert penman.Graph(
            [('b', 'instance', None), ('a', 'ARG', 'b')]
        ).top == 'b'
        assert penman.Graph(x1[1]).top == 'e2'

    def test_variables(self, x1):
        assert penman.Graph().variables() == set()
        assert penman.Graph([('a', 'ARG', 'b')]).variables() == set(['a'])
        assert penman.Graph(x1[1]).variables() == set(['e2', 'x1', '_1', 'e3'])

    def test_triples(self, x1):
        assert penman.Graph().triples() == []
        g = penman.Graph(x1[1])
        assert g.triples() == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
            ('e2', 'ARG1', 'x1'),
            ('x1', 'CARG', '"Abrams"'),
            ('_1', 'RSTR', 'x1'),
            ('e2', 'ARG2', 'e3'),
            ('e3', 'ARG1', 'x1')        
        ]
        assert g.triples(source='e2') == [
            ('e2', 'instance', '_try_v_1'),
            ('e2', 'ARG1', 'x1'),
            ('e2', 'ARG2', 'e3')
        ]
        assert g.triples(target='x1') == [
            ('e2', 'ARG1', 'x1'),
            ('_1', 'RSTR', 'x1'),
            ('e3', 'ARG1', 'x1')        
        ]
        assert g.triples(relation='instance') == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
        ]

    def test_edges(self, x1):
        assert penman.Graph().edges() == []
        g = penman.Graph(x1[1])
        assert g.edges() == [
            ('e2', 'ARG1', 'x1'),
            ('_1', 'RSTR', 'x1'),
            ('e2', 'ARG2', 'e3'),
            ('e3', 'ARG1', 'x1')        
        ]
        assert g.edges(source='e2') == [
            ('e2', 'ARG1', 'x1'),
            ('e2', 'ARG2', 'e3')        
        ]
        assert g.edges(source='e3') == [
            ('e3', 'ARG1', 'x1')
        ]
        assert g.edges(target='e3') == [
            ('e2', 'ARG2', 'e3')
        ]
        assert g.edges(relation='RSTR') == [
            ('_1', 'RSTR', 'x1')
        ]

    def test_attributes(self, x1):
        assert penman.Graph().attributes() == []
        g = penman.Graph(x1[1])
        assert g.attributes() == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
            ('x1', 'CARG', '"Abrams"')
        ]
        assert g.attributes(source='x1') == [
            ('x1', 'instance', 'named'),
            ('x1', 'CARG', '"Abrams"')
        ]
        assert g.attributes(target='named') == [
            ('x1', 'instance', 'named'),
        ]
        assert g.attributes(relation='instance') == [
            ('e2', 'instance', '_try_v_1'),
            ('x1', 'instance', 'named'),
            ('_1', 'instance', 'proper_q'),
            ('e3', 'instance', '_sleep_v_1'),
        ]

def test_loads():
    assert penman.loads('') == []
    assert penman.loads('# comment') == []
    assert penman.loads('# comment (n / not :ARG (g / graph))') == []
    assert len(penman.loads('(a / aaa)')) == 1
    assert len(penman.loads('(a / aaa)\n(b / bbb)')) == 2
    assert len(penman.loads(
        '# comment\n'
        '(a / aaa\n'
        '   :ARG1 (b / bbb))\n'
        '\n'
        '# another comment\n'
        '(b / bbb)\n'
    )) == 2

def test_loads_triples():
    assert penman.loads('', triples=True) == []
    assert len(penman.loads('instance(a, alpha)', triples=True)) == 1
    assert len(penman.loads('string(a, "alpha")', triples=True)) == 1

    gs = penman.loads('instance(a, alpha)ARG(a, b)', triples=True)
    assert len(gs) == 2
    assert gs[0].triples() == [('a', 'instance', 'alpha')]
    assert gs[1].triples() == [('a', 'ARG', 'b')]

    gs = penman.loads('instance(a, alpha)^ARG(a, b)', triples=True)
    assert len(gs) == 1
    assert gs[0].triples() == [('a', 'instance', 'alpha'), ('a', 'ARG', 'b')]

    class TestCodec(penman.PENMANCodec):
        TYPE_REL = 'test'
        TOP_VAR = 'TOP'
        TOP_REL = 'top'
    gs = penman.loads(
        'test(a, alpha)^test(b, beta)^ARG(a, b)^top(TOP, b)',
        triples=True, cls=TestCodec
    )
    assert len(gs) == 1
    assert gs[0].triples() == [
        ('a', 'test', 'alpha'),
        ('b', 'test', 'beta'),
        ('a', 'ARG', 'b')
    ]
    assert gs[0].top == 'b'

    gs = penman.loads(
        'test(a, alpha)^test(b, beta)^ARG(a, b)',
        triples=True, cls=TestCodec
    )
    assert gs[0].top == 'a'


def test_dumps():
    assert penman.dumps([]) == ''
    assert penman.dumps([penman.Graph([('a', 'instance', None)])]) == '(a)'
    assert penman.dumps([
        penman.Graph([('a', 'instance', None)]),
        penman.Graph([('b', 'instance', None)]),
    ]) == '(a)\n\n(b)'

def test_dumps_triples():
    assert penman.dumps(
        [penman.Graph([('a', 'instance', None)])], triples=True
    ) == 'instance(a, None)'
    assert penman.dumps(
        [penman.Graph([('a', 'instance', 'aaa')])], triples=True
    ) == 'instance(a, aaa)'
    assert penman.dumps(
        [penman.Graph([('a', 'instance', None), ('a', 'ARG', 'b')])],
        triples=True
    ) == 'instance(a, None) ^\nARG(a, b)'

    class TestCodec(penman.PENMANCodec):
        TYPE_REL = 'test'
        TOP_VAR = 'TOP'
        TOP_REL = 'top'
    assert penman.dumps(
        [penman.Graph([('a', 'ARG', 'b')])],
        triples=True, cls=TestCodec
    ) == 'top(TOP, a) ^\nARG(a, b)'
