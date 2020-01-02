
from penman.interface import (
    decode,
    loads,
    load,
    encode,
    dumps,
    dump,
)


def test_decode():
    assert decode('(a / alpha)').triples == [('a', ':instance', 'alpha')]


def test_loads():
    gs = loads('(a / alpha)(b / beta)')
    assert len(gs) == 2
    assert gs[0].triples == [('a', ':instance', 'alpha')]
    assert gs[1].triples == [('b', ':instance', 'beta')]


def test_load():
    pass


def test_encode():
    assert encode(decode('(a / alpha)')) == '(a / alpha)'


def test_dumps():
    assert dumps(loads('(a / alpha)(b / beta)')) == '(a / alpha)\n\n(b / beta)'


def test_dump():
    pass
