# -*- coding: utf-8 -*-

"""
Classes and functions for lexing PENMAN strings.
"""

from typing import Union, Iterable, Iterator, NamedTuple, Pattern, cast
import re
import logging

from penman.exceptions import DecodeError


# These are the regex patterns for parsing. They must not have any
# capturing groups. They are used during lexing and will be
# checked by name during parsing.
PATTERNS = {
    'STRING':     r'"[^"\\]*(?:\\.[^"\\]*)*"',
    'FLOAT':      r'''
      [-+]?
      (?:
        (?:(?:\d+\.\d*|\.\d+)  # .1   | 1.2
           (?:[eE][-+]?\d+)?)  # .1e2 | 1.2e3
       |\d+[eE][-+]?\d+        # 1e2
      )''',
    'INTEGER':    r'[-+]?\d+',
    'ALIGNMENT':  r'~(?:[a-zA-Z]\.?)?\d+(?:,\d+)*',
    # ROLE cannot be made up of COLON + SYMBOL because it then becomes
    # difficult to detect anonymous roles: (a : b) vs (a :b c)
    'ROLE':       r':[^\s()\/,:~^]*',
    'SYMBOL':     r'[^\s()\/,:~^]+',
    'LPAREN':     r'\(',
    'RPAREN':     r'\)',
    'SLASH':      r'\/',  # node label role
    'COMMA':      r',',   # used in triple conjunctions
    'CARET':      r'\^',  # used in triple conjunctions
    'UNEXPECTED': r'[^\s]'
}


def _compile(*names: str) -> Pattern[str]:
    pat = '\n|'.join('(?P<{}>{})'.format(name, PATTERNS[name])
                     for name in names)
    return re.compile(pat, flags=re.VERBOSE|re.UNICODE)


# The order matters in these pattern lists as more permissive patterns
# can short-circuit stricter patterns.
PENMAN_RE = _compile('STRING', 'FLOAT', 'INTEGER', 'ALIGNMENT', 'ROLE',
                     'SYMBOL', 'LPAREN', 'RPAREN', 'SLASH', 'UNEXPECTED')
TRIPLE_RE = _compile('STRING', 'FLOAT', 'INTEGER', 'SYMBOL',
                     'LPAREN', 'RPAREN', 'COMMA', 'CARET', 'UNEXPECTED')


class Token(NamedTuple):
    """
    A lexed token.
    """
    type: str    #: The token type.
    form: str    #: The matched string for the token.
    lineno: int  #: The line number the token appears on.
    offset: int  #: The character offset of the token.


class TokenIterator(Iterator[Token]):
    """
    An iterator of Tokens with L1 lookahead.
    """

    def __init__(self, iterator):
        try:
            self._next = next(iterator)
        except StopIteration:
            self._next = None
        self.iterator = iterator

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def peek(self) -> Union[Token, None]:
        """
        Return the next token but do not advance the iterator.

        If the iterator is exhausted, ``None`` is returned.
        """
        if self._next is None:
            return None
        else:
            return self._next

    def peek_type(self) -> Union[str, None]:
        """
        Return the next token's type but do not advance the iterator.

        If the iterator is exhausted, ``None`` is returned.

        The :meth:`peek` method is not so useful for things like
        while-loops as attempting to get the ``type`` attribute on a
        ``None`` value would raise an error, so this method satisfies
        that use-case:

        .. code:: python

           while tokens.peek_type() != 'RPAREN':
               ...
        """
        if self._next is None:
            return None
        else:
            return self._next.type

    def next(self) -> Token:
        """
        Advance the iterator and return the next token.

        Raises:
            :exc:`StopIteration`: if the iterator is already
                exhausted.
        """
        current = self._next
        try:
            self._next = next(self.iterator)
        except StopIteration:
            if current is None:
                raise
            self._next = None
        return current

    def expect(self, *choices):
        """
        Return the next token if its type is in *choices*.

        The iterator is advanced if successful.

        Raises:
            :exc:`DecodeError`: if the
                next token type is not in *choices*
        """
        token = self.next()
        if token.type not in choices:
            raise DecodeError(
                'Expected: {}'.format(', '.join(choices)),
                lineno=token.lineno,
                offset=token.offset,
                text=token.form)
        return token

    def accept(self, *choices):
        """
        Return the next token if its type is in *choices*.

        The iterator is advanced if successful. If unsuccessful,
        `None` is returned.
        """
        if self._next is not None and self._next.type in choices:
            return self.next()
        return None


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
            regex = re.compile(pattern, flags=re.UNICODE|re.VERBOSE)
        else:
            regex = pattern
    else:
        regex = PENMAN_RE

    logging.debug('Lexing with pattern:\n{}'.format(regex.pattern))

    tokens = _lex(lines, regex)
    return TokenIterator(tokens)


def _lex(lines: Iterable[str], regex: Pattern[str]) -> Iterator[Token]:
    for i, line in enumerate(lines, 1):
        for m in regex.finditer(line):
            if m.lastgroup is None:
                raise ValueError(
                    'Lexer pattern generated a match without a named '
                    'capturing group:\n{}'.format(regex.pattern))
            yield Token(m.lastgroup, m.group(), i, m.start())
