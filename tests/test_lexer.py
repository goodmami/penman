
from penman import _lexer as lexer


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
        'ROLE', 'ALIGNMENT', 'SYMBOL', 'ALIGNMENT',
        'RPAREN']
    assert _lex('# comment\n# (n / nope)\n(a / alpha)') == [
        'COMMENT', 'COMMENT', 'LPAREN', 'SYMBOL', 'SLASH', 'SYMBOL', 'RPAREN']


def test_lexing_issue_50():
    # https://github.com/goodmami/penman/issues/50
    assert [tok.type for tok in lexer.lex('(a :ROLE "a~b"~1)')] == [
        'LPAREN', 'SYMBOL', 'ROLE', 'STRING', 'ALIGNMENT', 'RPAREN']


def test_lex_triples():
    def _lex(s):
        return [tok.type for tok in lexer.lex(s, pattern=lexer.TRIPLE_RE)]

    assert _lex('') == []
    # SYMBOL may contain commas, so sometimes they get grouped together
    assert _lex('instance(a, alpha)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'SYMBOL', 'RPAREN']
    assert _lex('instance(a , alpha)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'SYMBOL', 'SYMBOL', 'RPAREN']
    assert _lex('instance(a ,alpha)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'SYMBOL', 'RPAREN']
    assert _lex('instance(a, alpha) ^ VAL(a, 1.0)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'SYMBOL', 'RPAREN',
        'SYMBOL',
        'SYMBOL', 'LPAREN', 'SYMBOL', 'SYMBOL', 'RPAREN']
    assert _lex('instance(a, 1,000)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'SYMBOL', 'RPAREN']
    assert _lex('instance(a,1,000)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'RPAREN']
    assert _lex('role(a,b) ^ role(b,c)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'RPAREN',
        'SYMBOL',
        'SYMBOL', 'LPAREN', 'SYMBOL', 'RPAREN']
    assert _lex('role(a,b)^role(b,c)') == [
        'SYMBOL', 'LPAREN', 'SYMBOL', 'RPAREN',
        'SYMBOL', 'LPAREN', 'SYMBOL', 'RPAREN']


def test_TokenIterator():
    pass  # TODO: write tests for expect() and accept()


def test_nonbreaking_space_issue_99():
    # https://github.com/goodmami/penman/issues/99
    assert [tok.type for tok in lexer.lex('1 2')] == ['SYMBOL', 'SYMBOL']
    assert [tok.type for tok in lexer.lex('1\t2')] == ['SYMBOL', 'SYMBOL']
    assert [tok.type for tok in lexer.lex('1\n2')] == ['SYMBOL', 'SYMBOL']
    assert [tok.type for tok in lexer.lex('1\r2')] == ['SYMBOL', 'SYMBOL']
    assert [tok.type for tok in lexer.lex('1\u00a02')] == ['SYMBOL']
    assert [tok.type for tok in lexer.lex('あ　い')] == ['SYMBOL']


def test_unterminated_string_issue_143():
    # https://github.com/goodmami/penman/issues/143
    # unmatched quotes result in unexpected tokens
    assert [tok.type for tok in lexer.lex('(a :op ")')] == [
        'LPAREN', 'SYMBOL', 'ROLE', 'UNEXPECTED', 'RPAREN'
    ]
    assert [tok.type for tok in lexer.lex('(a :op1 " :op2 "foo")')] == [
        'LPAREN', 'SYMBOL', 'ROLE', 'STRING', 'SYMBOL', 'UNEXPECTED', 'RPAREN'
    ]
    # also disallow quotes in role names
    assert [tok.type for tok in lexer.lex('(a :" b)')] == [
        'LPAREN', 'SYMBOL', 'ROLE', 'UNEXPECTED', 'SYMBOL', 'RPAREN'
    ]
