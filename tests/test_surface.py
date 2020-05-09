
import penman
from penman.surface import (
    Alignment,
    RoleAlignment,
    alignments,
    role_alignments,
)

codec = penman.PENMANCodec()


def test_alignments(isi_aligned):
    g = codec.decode('(a :ARG~1 (b / beta~2))')
    assert alignments(g) == {
        ('b', ':instance', 'beta'): Alignment((2,)),
    }
    assert role_alignments(g) == {
        ('a', ':ARG', 'b'): RoleAlignment((1,)),
    }
    assert codec.encode(g, indent=None) == '(a :ARG~1 (b / beta~2))'

    g = codec.decode(isi_aligned[0])
    assert alignments(g) == {
        ('d', ':instance', 'drive-01'): Alignment((2,), prefix='e.'),
        ('h', ':instance', 'he'): Alignment((1,), prefix='e.'),
        ('c', ':instance', 'care-04'): Alignment((3,), prefix='e.'),
    }
    assert role_alignments(g) == {}
    assert codec.encode(g) == (
        '(d / drive-01~e.2\n'
        '   :ARG0 (h / he~e.1)\n'
        '   :manner (c / care-04~e.3\n'
        '              :polarity -))')
