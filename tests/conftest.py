
import pytest

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
            ('e2', 'ARG1', 'x1'),
            ('x1', 'instance', 'named'),
            ('x1', 'CARG', '"Abrams"'),
            ('_1', 'RSTR', 'x1'),
            ('_1', 'instance', 'proper_q'),
            ('e2', 'ARG2', 'e3'),
            ('e3', 'instance', '_sleep_v_1'),
            ('e3', 'ARG1', 'x1'),
        ]
    )


@pytest.fixture
def x2():
    return (
        '(10000 / _bark_v_1\n'
        '       :ARG1 (10001 / _dog_n_1\n'
        '                    :RSTR-of (10002 / udef_q)))',
        [
            (10000, 'instance', '_bark_v_1'),
            (10000, 'ARG1', 10001),
            (10001, 'instance', '_dog_n_1'),
            (10002, 'RSTR', 10001),
            (10002, 'instance', 'udef_q'),
        ]
    )
