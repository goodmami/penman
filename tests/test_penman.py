
import pytest

from penman import (
    parse,
    parse_triples,
    interpret,
    decode,
    loads,
    load,
    format,
    format_triples,
    configure,
    encode,
    dumps,
    dump,
    DecodeError,
)


def test_decode():
    assert decode('(a / alpha)').triples == [('a', ':instance', 'alpha')]


def test_loads():
    gs = loads('(a / alpha)(b / beta)')
    assert len(gs) == 2
    assert gs[0].triples == [('a', ':instance', 'alpha')]
    assert gs[1].triples == [('b', ':instance', 'beta')]


def test_load(tmp_path):
    f = tmp_path / 'test_load1'
    f.write_text('(a / alpha)(b / beta)', encoding='utf-8')
    gs = load(f)
    assert len(gs) == 2
    assert gs[0].triples == [('a', ':instance', 'alpha')]
    assert gs[1].triples == [('b', ':instance', 'beta')]

    with f.open(encoding='utf-8') as fh:
        assert load(fh) == gs


def test_encode():
    assert encode(decode('(a / alpha)')) == '(a / alpha)'


def test_dumps():
    assert dumps(loads('(a / alpha)(b / beta)')) == '(a / alpha)\n\n(b / beta)'


def test_dump(tmp_path):
    gs = loads('(a / alpha)(b / beta)')
    f1 = tmp_path / 'test_dump1'
    f2 = tmp_path / 'test_dump2'
    dump(gs, f1)
    with f2.open('w', encoding='utf-8') as fh:
        dump(gs, fh)
    assert f1.read_text(encoding='utf-8') == f2.read_text(encoding='utf-8')


def test_parse():
    assert parse('()') == (None, [])
    assert parse('(a)') == ('a', [])
    assert parse('(a / )') == ('a', [('/', None)])
    assert parse('(a / alpha)') == ('a', [('/', 'alpha')])
    assert parse('(a : b)') == ('a', [(':', 'b')])
    assert parse('(a : ())') == ('a', [(':', (None, []))])
    assert parse('(a : (b))') == ('a', [(':', ('b', []))])
    assert parse('(a / alpha :ARG (b / beta))') == (
        'a', [('/', 'alpha'),
              (':ARG', ('b', [('/', 'beta')]))])
    assert parse('(a :ARG-of b)') == ('a', [(':ARG-of', 'b')])
    assert parse('(a :ARG~1 b~2)') == ('a', [(':ARG~1', 'b~2')])
    # https://github.com/goodmami/penman/issues/50
    assert parse('(a :ARG "str~ing")') == ('a', [(':ARG', '"str~ing"')])
    assert parse('(a :ARG "str~ing"~1)') == ('a', [(':ARG', '"str~ing"~1')])


def test_format():
    assert format((None, [])) == '()'
    assert format(('a', [])) == '(a)'
    assert format(('a', [('/', None)])) == '(a /)'
    assert format(('a', [('/', '')])) == '(a /)'
    assert format(('a', [('/', 'alpha')])) == '(a / alpha)'
    assert format(('a', [('', 'b')])) == '(a : b)'
    assert format(('a', [(':', 'b')])) == '(a : b)'
    assert format(('a', [(':', (None, []))])) == '(a : ())'
    assert format(('a', [('', ('b', []))])) == '(a : (b))'
    assert format(
        ('a', [('/', 'alpha'),
               ('ARG', ('b', [('/', 'beta')]))]),
        indent=None
    ) == '(a / alpha :ARG (b / beta))'
    assert format(('a', [('ARG-of', 'b')])) == '(a :ARG-of b)'
    assert format(('a', [(':ARG-of', 'b')])) == '(a :ARG-of b)'
    assert format(('a', [('ARG~1', 'b~2')])) == '(a :ARG~1 b~2)'


def test_parse_triples():
    assert parse_triples('role(a,b)') == [
        ('a', ':role', 'b')]
    assert parse_triples('role(a, b)') == [
        ('a', ':role', 'b')]
    assert parse_triples('role(a ,b)') == [
        ('a', ':role', 'b')]
    assert parse_triples('role(a , b)') == [
        ('a', ':role', 'b')]
    assert parse_triples('role(a,)') == [
        ('a', ':role', None)]
    assert parse_triples('role(a ,)') == [
        ('a', ':role', None)]
    assert parse_triples('role(a,b)^role(b,c)') == [
        ('a', ':role', 'b'), ('b', ':role', 'c')]
    assert parse_triples('role(a, b) ^role(b, c)') == [
        ('a', ':role', 'b'), ('b', ':role', 'c')]
    assert parse_triples('role(a, b) ^ role(b, c)') == [
        ('a', ':role', 'b'), ('b', ':role', 'c')]
    with pytest.raises(DecodeError):
        decode('role')
    with pytest.raises(DecodeError):
        decode('role(')
    with pytest.raises(DecodeError):
        decode('role(a')
    with pytest.raises(DecodeError):
        decode('role()')
    with pytest.raises(DecodeError):
        decode('role(a,')
    with pytest.raises(DecodeError):
        decode('role(a ^')
    with pytest.raises(DecodeError):
        decode('role(a b')
    with pytest.raises(DecodeError):
        decode('role(a b)')


def test_format_triples():
    triples = format_triples([
        ('a', ':instance', 'alpha'),
        ('a', ':ARG0', 'b'),
        ('b', ':instance', 'beta'),
        ('g', ':ARG0', 'a'),
        ('g', ':instance', 'gamma'),
        ('g', ':ARG1', 'b'),
    ])
    assert triples == (
        'instance(a, alpha) ^\n'
        'ARG0(a, b) ^\n'
        'instance(b, beta) ^\n'
        'ARG0(g, a) ^\n'
        'instance(g, gamma) ^\n'
        'ARG1(g, b)'
    )


def test_format_with_parameters():
    # no indent
    assert format(
        ('a', [('/', 'alpha'), ('ARG', ('b', [('/', 'beta')]))]),
        indent=None
    ) == '(a / alpha :ARG (b / beta))'
    # default (adaptive) indent
    assert format(
        ('a', [('/', 'alpha'), ('ARG', ('b', [('/', 'beta')]))]),
        indent=-1
    ) == ('(a / alpha\n'
          '   :ARG (b / beta))')
    # fixed indent
    assert format(
        ('a', [('/', 'alpha'), ('ARG', ('b', [('/', 'beta')]))]),
        indent=6
    ) == ('(a / alpha\n'
          '      :ARG (b / beta))')
    # default compactness of attributes
    assert format(
        ('a', [('/', 'alpha'),
               ('polarity', '-'),
               ('ARG', ('b', [('/', 'beta')]))]),
        compact=False
    ) == ('(a / alpha\n'
          '   :polarity -\n'
          '   :ARG (b / beta))')
    # compact of attributes
    assert format(
        ('a', [('/', 'alpha'),
               ('polarity', '-'),
               ('ARG', ('b', [('/', 'beta')]))]),
        compact=True
    ) == ('(a / alpha :polarity -\n'
          '   :ARG (b / beta))')
    # compact of attributes (only initial)
    assert format(
        ('a', [('/', 'alpha'),
               ('polarity', '-'),
               ('ARG', ('b', [('/', 'beta')])),
               ('mode', 'expressive')]),
        compact=True
    ) == ('(a / alpha :polarity -\n'
          '   :ARG (b / beta)\n'
          '   :mode expressive)')


def test_interpret():
    t = parse('(a / alpha :ARG0 (b / beta) :ARG0-of (g / gamma :ARG1 b))')
    g = interpret(t)
    assert g.triples == [
        ('a', ':instance', 'alpha'),
        ('a', ':ARG0', 'b'),
        ('b', ':instance', 'beta'),
        ('g', ':ARG0', 'a'),
        ('g', ':instance', 'gamma'),
        ('g', ':ARG1', 'b'),
    ]


def test_configure():
    g = decode('(a / alpha :ARG0 (b / beta) :ARG0-of (g / gamma :ARG1 b))')
    t = configure(g)
    assert t.node == (
        'a', [('/', 'alpha'),
              (':ARG0', ('b', [('/', 'beta')])),
              (':ARG0-of', ('g', [('/', 'gamma'),
                                  (':ARG1', 'b')]))])
