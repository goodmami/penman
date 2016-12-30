
import penman

def test_decode():
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
        ('a', None, 'b'),
        ('b', 'instance', None)
    ]
    assert g.top == 'a'

    # inverted unlabeled edge
    g = decode('(b :-of (a))')
    assert g.triples() == [
        ('b', 'instance', None),
        ('a', None, 'b'),
        ('a', 'instance', None)
    ]
    assert g.top == 'b'

    # labeled edge to unlabeled node
    g = decode('(a :ARG (b))')
    assert g.triples() == [
        ('a', 'instance', None),
        ('a', 'ARG', 'b'),
        ('b', 'instance', None)
    ]
    assert g.top == 'a'

    # inverted edge
    g = decode('(b :ARG-of (a))')
    assert g.triples() == [
        ('b', 'instance', None),
        ('a', 'ARG', 'b'),
        ('a', 'instance', None)
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
    g = decode(
        '(e2 / _try_v_1'
        '    :ARG1 (x1 / named'
        '              :CARG "Abrams"'
        '              :RSTR-of (_1 / proper_q))'
        '    :ARG2 (e3 / _sleep_v_1'
        '              :ARG1 x1))')
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
    

def test_encode():
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
        ('a', None, 'b'),
        ('b', 'instance', None)
    ])
    assert encode(g) == '(a : (b))'

    # inverted unlabeled edge
    g = penman.Graph([
        ('b', 'instance', None),
        ('a', None, 'b'),
        ('a', 'instance', None)
    ])
    assert encode(g) == '(b :-of (a))'

    # labeled edge to unlabeled node
    g = penman.Graph([
        ('a', 'instance', None),
        ('a', 'ARG', 'b'),
        ('b', 'instance', None)
    ])
    assert encode(g) == '(a :ARG (b))'

    # inverted edge
    g = penman.Graph([
        ('b', 'instance', None),
        ('a', 'ARG', 'b'),
        ('a', 'instance', None)
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

    # fuller example
    g = penman.Graph([
        ('e2', 'instance', '_try_v_1'),
        ('e2', 'ARG1', 'x1'),
        ('e2', 'ARG2', 'e3'),
        ('x1', 'instance', 'named'),
        ('x1', 'CARG', '"Abrams"'),
        ('_1', 'RSTR', 'x1'),
        ('e3', 'instance', '_sleep_v_1'),
        ('e3', 'ARG1', 'x1'),
        ('_1', 'instance', 'proper_q')
    ])
    assert encode(g) == (
        '(e2 / _try_v_1\n'
        '    :ARG1 (x1 / named\n'
        '              :CARG "Abrams"\n'
        '              :RSTR-of (_1 / proper_q))\n'
        '    :ARG2 (e3 / _sleep_v_1\n'
        '              :ARG1 x1))'
    )

    # reentrancy under inversion
    g = penman.Graph([
        ('a', 'instance', 'aaa'),
        ('a', 'ARG1', 'b'),
        ('b', 'instance', 'bbb'),
        ('c', 'instance', 'ccc'),
        ('c', 'ARG1', 'b2'),
        ('c', 'ARG2', 'a'),
        ('b2', 'instance', 'bbb')
    ])
    assert encode(g) == (
        '(a / aaa\n'
        '   :ARG1 (b / bbb)\n'
        '   :ARG2-of (c / ccc\n'
        '               :ARG1 (b2 / bbb)))'
    )

def test_to_penman_with_indent():
    encode = penman.encode
    g = penman.Graph([
        ('a', 'instance', 'aaa'),
        ('a', 'ARG1', 'b'),
        ('b', 'instance', 'bbb'),
        ('b', 'ARG1', 'c'),
        ('c', 'instance', 'ccc')
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

def test_graph_inspection():
    g = penman.decode(
        '(e2 / _try_v_1'
        '    :ARG1 (x1 / named'
        '              :CARG "Abrams"'
        '              :RSTR-of (_1 / proper_q))'
        '    :ARG2 (e3 / _sleep_v_1'
        '              :ARG1 x1))'
    )
    assert g.top == 'e2'
    assert g.variables() == set(['e2', 'x1', '_1', 'e3'])
    # assert g.instances() == set(['e2', 'x1', '_1', 'e3'])
    # assert g.instances('named') == set(['x1'])
    assert g.concepts() == set([
        '_try_v_1',
        'named',
        'proper_q',
        '_sleep_v_1'
    ])
    assert sorted(g.constants()) == [
        '"Abrams"'
    ]
    assert g.edges(source='e2')  == [
        ('e2', 'ARG1', 'x1'),
        ('e2', 'ARG2', 'e3')        
    ]
    assert g.edges(source='e3') == [
        ('e3', 'ARG1', 'x1')
    ]
    assert g.edges(target='e3') == [
        ('e2', 'ARG2', 'e3')
    ]

