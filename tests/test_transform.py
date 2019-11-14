
from penman.model import Model
from penman.models.amr import model as amr_model
from penman.codec import PENMANCodec
from penman.transform import (
    canonicalize_roles,
    reify_edges,
    contract_edges,
    reify_attributes,
    indicate_branches,
)


def_model = Model()
def_codec = PENMANCodec(model=def_model)
amr_codec = PENMANCodec(model=amr_model)


def test_canonicalize_roles_default_codec():
    parse = def_codec.parse
    norm = lambda t: canonicalize_roles(t, def_model)
    format = lambda t: def_codec.format(t, indent=None)

    t = norm(parse('(a / alpha :ARG1 (b / beta))'))
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :ARG1-of-of (b / beta))'))
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :mod-of (b / beta))'))
    assert format(t) == '(a / alpha :mod-of (b / beta))'


def test_canonicalize_roles_amr_codec():
    parse = amr_codec.parse
    norm = lambda t: canonicalize_roles(t, amr_model)
    format = lambda t: amr_codec.format(t, indent=None)

    t = norm(parse('(a / alpha :ARG1 (b / beta))'))
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :ARG1-of-of (b / beta))'))
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :mod-of (b / beta))'))
    assert format(t) == '(a / alpha :domain (b / beta))'


def test_reify_edges_default_codec():
    decode = def_codec.decode
    norm = lambda g: reify_edges(g, def_model)
    encode = lambda g: def_codec.encode(g, indent=None)

    g = norm(decode('(a / alpha :mod 5)'))
    assert encode(g) == '(a / alpha :mod 5)'

    g = norm(decode('(a / alpha :mod-of (b / beta))'))
    assert encode(g) == '(a / alpha :mod-of (b / beta))'


def test_reify_edges_amr_codec():
    decode = amr_codec.decode
    norm = lambda g: reify_edges(g, amr_model)
    encode = lambda g: amr_codec.encode(g, indent=None)

    g = norm(decode('(a / alpha :mod 5)'))
    assert encode(g) == '(a / alpha :ARG1-of (_ / have-mod-91 :ARG2 5))'

    g = norm(decode('(a / alpha :mod-of (b / beta))'))
    assert encode(g) == '(a / alpha :ARG2-of (_ / have-mod-91 :ARG1 (b / beta)))'

    g = norm(decode('(a / alpha :mod-of (b / beta :polarity -))'))
    assert encode(g) == (
        '(a / alpha :ARG2-of (_ / have-mod-91 '
        ':ARG1 (b / beta :ARG1-of (_2 / have-polarity-91 :ARG2 -))))')

    g = norm(decode('(a / alpha :mod-of~1 (b / beta~2 :polarity -))'))
    assert encode(g) == (
        '(a / alpha :ARG2-of (_ / have-mod-91~1 '
        ':ARG1 (b / beta~2 :ARG1-of (_2 / have-polarity-91 :ARG2 -))))')


def contract_edges():
    pass


def reify_attributes():
    pass


def indicate_branches():
    pass
