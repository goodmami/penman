
"""
Base classes for epigraphical markers.
"""

from typing import List


class Epidatum(object):
    __slots__ = ()

    #: The :attr:`mode` attribute specifies what the Epidatum annotates:
    #:
    #:  * ``mode=0`` -- unspecified
    #:  * ``mode=1`` -- role epidata
    #:  * ``mode=2`` -- target epidata
    mode = 0


Epidata = List[Epidatum]
