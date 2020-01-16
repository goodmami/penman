# -*- coding: utf-8 -*-

"""
Classes and functions for lexing PENMAN strings.
"""

from typing import Union, Iterable, Iterator, NamedTuple, Pattern
import re
import logging

from penman.exceptions import DecodeError


logger = logging.getLogger(__name__)


# These are the regex patterns for parsing. They must not have any
# capturing groups. They are used during lexing and will be
# checked by name during parsing.
PATTERNS = {
    'COMMENT':    r'\#.*$',
    'STRING':     r'"[^"\\]*(?:\\.[^"\\]*)*"',
    'ALIGNMENT':  r'~(?:[a-z]\.?)?[0-9]+(?:,[0-9]+)*',
    # ROLE cannot be made up of COLON + SYMBOL because it then becomes
    # difficult to detect anonymous roles: (a : b) vs (a :b c)
    'ROLE':       r':[^\s()\/:~]*',
    'SYMBOL':     r'[^\s()\/:~]+',
    'LPAREN':     r'\(',
    'RPAREN':     r'\)',
    'SLASH':      r'\/',  # concept (node label) role
    'UNEXPECTED': r'[^\s]'
}


def _compile(*names: str) -> Pattern[str]:
    pat = '\n|'.join(f'(?P<{name}>{PATTERNS[name]})' for name in names)
    return re.compile(pat, flags=re.VERBOSE)


# The order matters in these pattern lists as more permissive patterns
# can short-circuit stricter patterns.
PENMAN_RE = _compile('COMMENT',
                     'STRING',
                     'LPAREN', 'RPAREN', 'SLASH',
                     'ROLE', 'SYMBOL', 'ALIGNMENT',
                     'UNEXPECTED')
TRIPLE_RE = _compile('COMMENT',
                     'STRING',
                     'LPAREN', 'RPAREN',
                     'SYMBOL',
                     'UNEXPECTED')


class Token(NamedTuple):
    """
    A lexed token.
    """
    type: str    #: The token type.
    text: str    #: The matched string for the token.
    lineno: int  #: The line number the token appears on.
    offset: int  #: The character offset of the token.
    line: str    #: The line the token appears in.


class TokenIterator(Iterator[Token]):
    """
    An iterator of Tokens with L1 lookahead.
    """

    def __init__(self, iterator):
        try:
            self._next = next(iterator)
        except StopIteration:
            self._next = None
        self._last = None
        self.iterator = iterator

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __bool__(self):
        return self._next is not None

    def peek(self) -> Token:
        """
        Return the next token but do not advance the iterator.

        If the iterator is exhausted then a
        :exc:`~penman.exceptions.DecodeError` is raised.
        """
        if self._next is None:
            raise self.error('Unexpected end of input')
        return self._next

    def next(self) -> Token:
        """
        Advance the iterator and return the next token.

        Raises:
            StopIteration
                If the iterator is already exhausted.
        """
        current = self._next
        try:
            self._next = next(self.iterator)
        except StopIteration:
            if current is None:
                raise
            self._next = None
        self._last = current
        return current

    def expect(self, *choices):
        """
        Return the next token if its type is in *choices*.

        The iterator is advanced if successful.

        Raises:
            ~penman.exceptions.DecodeError
                If the next token type is not in *choices*.
        """
        try:
            token = self.next()
        except StopIteration:
            raise self.error('Unexpected end of input')
        if token.type not in choices:
            raise self.error('Expected: {}'.format(', '.join(choices)),
                             token=token)
        return token

    def accept(self, *choices):
        """
        Return the next token if its type is in *choices*.

        The iterator is advanced if successful. If unsuccessful,
        ``None`` is returned.
        """
        if self._next is not None and self._next.type in choices:
            return self.next()
        return None

    def error(self, message: str, token=None) -> DecodeError:
        if token is None:
            type = line = None
            if self._last is not None:
                lineno = self._last.lineno
                offset = self._last.offset + len(self._last.text)
                line = self._last.line
            else:
                lineno = offset = 0
        else:
            type, _, lineno, offset, line = token

        return DecodeError(message, lineno=lineno, offset=offset, text=line)


def lex(lines: Union[Iterable[str], str],
        pattern: Union[Pattern[str], str] = None) -> TokenIterator:
    """
    Yield PENMAN tokens matched in *lines*.

    By default, this lexes strings in *lines* using the basic pattern
    for PENMAN graphs. If *pattern* is given, it is used for lexing
    instead.

    Args:
        lines: iterable of lines to lex
        pattern: pattern to use for lexing instead of the default ones
    Returns:
        A :class:`TokenIterator` object
    """
    if isinstance(lines, str):
        lines = lines.splitlines()
    if pattern is not None:
        if isinstance(pattern, str):
            regex = re.compile(pattern, flags=re.VERBOSE)
        else:
            regex = pattern
    else:
        regex = PENMAN_RE

    tokens = _lex(lines, regex)
    return TokenIterator(tokens)


def _lex(lines: Iterable[str], regex: Pattern[str]) -> Iterator[Token]:
    debug = logger.isEnabledFor(logging.DEBUG)
    for i, line in enumerate(lines, 1):
        if debug:
            logger.debug('Line %d: %r', i, line)
        matches = regex.finditer(line)
        for m in matches:
            typ = m.lastgroup
            val = m.group()
            if typ is None:
                raise ValueError(
                    'Lexer pattern generated a match without a named '
                    f'capturing group:\n{regex.pattern}')
            token = Token(typ, val, i, m.start(), line)
            if debug:
                logger.debug(token)
            yield token
