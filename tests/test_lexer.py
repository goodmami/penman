
from penman import lexer

def test_lex_penman():
    def _lex(s):
        return [tok.type for tok in lexer.lex(s)]

    assert _lex('') == []
    assert _lex('(a / alpha)') == [
        'LPAREN', 'SYMBOL', 'SLASH', 'SYMBOL', 'RPAREN']
    assert _lex('(a/alpha\n  :ROLE b)') == [
        'LPAREN', 'SYMBOL', 'SLASH', 'SYMBOL',
        'ROLE', 'SYMBOL', 'RPAREN']
    assert _lex(['(a / alpha', '  :ROLE b)']) == _lex('(a/alpha\n  :ROLE b)')
    assert _lex('(a :INT 1 :STR "hi there" :FLOAT -1.2e3)') == [
        'LPAREN', 'SYMBOL',
        'ROLE', 'SYMBOL',
        'ROLE', 'STRING',
        'ROLE', 'SYMBOL',
        'RPAREN']
    assert _lex('(a :ROLE~e.1,2 b~3)') == [
        'LPAREN', 'SYMBOL',
        'ROLE', 'ALIGNMENT',
        'SYMBOL', 'ALIGNMENT',
        'RPAREN']
    assert _lex('# comment\n# (n / nope)\n(a / alpha)') == [
        'COMMENT', 'COMMENT', 'LPAREN', 'SYMBOL', 'SLASH', 'SYMBOL', 'RPAREN']


def test_lex_triples():
    def _lex(s):
        return [tok.type for tok in lexer.lex(s, pattern=lexer.TRIPLE_RE)]

    assert _lex('') == []
    assert _lex('instance(a, alpha)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'COMMA', 'SYMBOL', 'RPAREN']
    assert _lex('instance(a, alpha) ^ VAL(a, 1.0)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'COMMA', 'SYMBOL', 'RPAREN',
        'CARET',
        'SYMBOL', 'LPAREN', 'SYMBOL', 'COMMA', 'SYMBOL', 'RPAREN']

def test_TokenIterator():
    pass  # TODO: write tests for expect() and accept()
