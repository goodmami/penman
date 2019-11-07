
import pytest

import penman
from penman import surface

codec = penman.PENMANCodec()


def test_alignments(isi_aligned):
    g = codec.decode(isi_aligned[0])
    assert surface.alignments(g) == {
        ('d', ':instance', 'drive-01'): surface.Alignment((2,), prefix='e.'),
        ('h', ':instance', 'he'): surface.Alignment((1,), prefix='e.'),
        ('c', ':instance', 'care-04'): surface.Alignment((3,), prefix='e.'),
    }
    assert surface.role_alignments(g) == {}
