
import penman

def test_from_penman():
    parse = penman.Graph.from_penman
    g = parse('(h / hi)')
    assert g.to_triples() == [('h', 'instance-of', 'hi')]
    g = parse('(b / bark :ARG0 (d / dog))')
    assert sorted(g.to_triples()) == [
        ('b', 'ARG0', 'd'),
        ('b', 'instance-of', 'bark'),
        ('d', 'instance-of', 'dog')
    ]
    g = parse(
        '(e2 / _try_v_1'
        '    :ARG1 (x1 / named'
        '              :CARG "Abrams"'
        '              :RSTR-of (_1 / proper_q))'
        '    :ARG2 (e3 / _sleep_v_1'
        '              :ARG1 x1))')
    assert sorted(g.to_triples()) == [
        ('_1', 'instance-of', 'proper_q'),
        ('e2', 'ARG1', 'x1'),
        ('e2', 'ARG2', 'e3'),
        ('e2', 'instance-of', '_try_v_1'),
        ('e3', 'ARG1', 'x1'),
        ('e3', 'instance-of', '_sleep_v_1'),
        ('x1', 'CARG', '"Abrams"'),
        ('x1', 'RSTR-of', '_1'),
        ('x1', 'instance-of', 'named')
    ]

def test_to_penman():
    load = penman.Graph.from_triples
    g = load([
        ('h', 'instance-of', 'hi')
    ])
    assert g.to_penman() == '(h / hi)'
    g = load([
        ('hi', 'instance', 'h')
    ])
    assert g.to_penman() == '(hi :instance h)'
    assert g.to_penman(top='h') == '(h / hi)'
    g = load([
        ('b', 'ARG0', 'd'),
        ('b', 'instance-of', 'bark'),
        ('d', 'instance-of', 'dog')
    ])
    assert g.to_penman() == (
        '(b / bark\n'
        '   :ARG0 (d / dog))'
    )
    g = load([
        ('e2', 'instance-of', '_try_v_1'),
        ('e2', 'ARG1', 'x1'),
        ('e2', 'ARG2', 'e3'),
        ('x1', 'instance-of', 'named'),
        ('x1', 'CARG', '"Abrams"'),
        ('x1', 'RSTR-of', '_1'),
        ('e3', 'instance-of', '_sleep_v_1'),
        ('e3', 'ARG1', 'x1'),
        ('_1', 'instance-of', 'proper_q')
    ])
    assert g.to_penman() == (
        '(e2 / _try_v_1\n'
        '    :ARG1 (x1 / named\n'
        '              :CARG "Abrams"\n'
        '              :RSTR-of (_1 / proper_q))\n'
        '    :ARG2 (e3 / _sleep_v_1\n'
        '              :ARG1 x1))'
    )
    g = load([
        ('a', 'instance-of', 'aaa'),
        ('a', 'ARG1', 'b'),
        ('b', 'instance-of', 'bbb'),
        ('c', 'instance-of', 'ccc'),
        ('c', 'ARG1', 'b2'),
        ('c', 'ARG2', 'a'),
        ('b2', 'instance-of', 'bbb')
    ])
    assert g.to_penman() == (
        '(a / aaa\n'
        '   :ARG1 (b / bbb)\n'
        '   :ARG2-of (c / ccc\n'
        '               :ARG1 (b2 / bbb)))'
    )

def test_to_penman_with_indent():
    g = penman.Graph.from_triples([
        ('a', 'instance-of', 'aaa'),
        ('a', 'ARG1', 'b'),
        ('b', 'instance-of', 'bbb'),
        ('b', 'ARG1', 'c'),
        ('c', 'instance-of', 'ccc')
    ])
    assert g.to_penman(indent=True) == (
        '(a / aaa\n'
        '   :ARG1 (b / bbb\n'
        '            :ARG1 (c / ccc)))'
    )
    assert g.to_penman(indent=False) == (
        '(a / aaa :ARG1 (b / bbb :ARG1 (c / ccc)))'
    )
    assert g.to_penman(indent=None) == (
        '(a / aaa :ARG1 (b / bbb :ARG1 (c / ccc)))'
    )
    assert g.to_penman(indent=0) == (
        '(a / aaa\n'
        ':ARG1 (b / bbb\n'
        ':ARG1 (c / ccc)))'
    )
    assert g.to_penman(indent=2) == (
        '(a / aaa\n'
        '  :ARG1 (b / bbb\n'
        '    :ARG1 (c / ccc)))'
    )

def test_graph_inspection():
    g = penman.Graph.from_penman(
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
        ('e2', 'ARG2', 'e3'),
        ('_sleep_v_1', 'instance', 'e3')
    ]

