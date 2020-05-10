
import pytest


@pytest.fixture(scope='module')
def mini_amr():
    return {
        'roles': {
            ':ARG0': {'type': 'frame'},
            ':ARG1': {'type': 'frame'},
            ":accompanier": {"type": "general"},
            ":domain": {"type": "general"},
            ":consist-of": {"type": "general"},
            ":mod": {"type": "general"},
            ":op[0-9]+": {"type": "op"},
        },
        'normalizations': {
            ':mod-of': ':domain',
            ':domain-of': ':mod',
        },
        'reifications': [
            (':accompanier', 'accompany-01', ':ARG0', ':ARG1'),
            (':mod', 'have-mod-91', ':ARG1', ':ARG2')
        ]
    }


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
            ('e2', ':instance', '_try_v_1'),
            ('e2', ':ARG1', 'x1'),
            ('x1', ':instance', 'named'),
            ('x1', ':CARG', '"Abrams"'),
            ('_1', ':RSTR', 'x1'),
            ('_1', ':instance', 'proper_q'),
            ('e2', ':ARG2', 'e3'),
            ('e3', ':instance', '_sleep_v_1'),
            ('e3', ':ARG1', 'x1'),
        ]
    )


@pytest.fixture
def isi_aligned():
    """He drives carelessly."""
    return (
        '(d / drive-01~e.2\n'
        '   :ARG0 (h / he~e.1)\n'
        '   :manner (c / care-04~e.3\n'
        '              :polarity -))',
        [
            ('d', ':instance', 'drive-01'),
            ('d', ':ARG0', 'h'),
            ('h', ':instance', 'he'),
            ('d', ':manner', 'c'),
            ('c', ':instance', 'care-04'),
            ('c', ':polarity', '-')
        ]
    )
