# -*- coding: utf-8 -*-


class PenmanError(Exception):
    """Base class for errors in the Penman package."""


class EncodeError(PenmanError):
    """Raises when encoding PENMAN-notation fails."""


class DecodeError(PenmanError):
    """Raised when decoding PENMAN-notation fails."""

    def __init__(self, *args, **kwargs):
        # Python2 doesn't allow parameters like:
        #   (*args, key=val, **kwargs)
        # so do this manaully.
        string = pos = None
        if 'string' in kwargs:
            string = kwargs['string']
            del kwargs['string']
        if 'pos' in kwargs:
            pos = kwargs['pos']
            del kwargs['pos']
        super(DecodeError, self).__init__(*args, **kwargs)
        self.string = string
        self.pos = pos

    def __str__(self):
        if isinstance(self.pos, slice):
            loc = ' in span {}:{}'.format(self.pos.start, self.pos.stop)
        else:
            loc = ' at position {}'.format(self.pos)
        return Exception.__str__(self) + loc
