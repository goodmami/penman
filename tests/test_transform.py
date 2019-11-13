
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
    format = lambda t: def_codec.format(t, indent=None)

    t = parse('(a / alpha :ARG1 (b / beta))')
    canonicalize_roles(t, def_model)
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = parse('(a / alpha :ARG1-of-of (b / beta))')
    canonicalize_roles(t, def_model)
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = parse('(a / alpha :mod-of (b / beta))')
    canonicalize_roles(t, def_model)
    assert format(t) == '(a / alpha :mod-of (b / beta))'


def test_canonicalize_roles_amr_codec():
    parse = amr_codec.parse
    format = lambda t: amr_codec.format(t, indent=None)

    t = parse('(a / alpha :ARG1 (b / beta))')
    canonicalize_roles(t, amr_model)
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = parse('(a / alpha :ARG1-of-of (b / beta))')
    canonicalize_roles(t, amr_model)
    assert format(t) == '(a / alpha :ARG1 (b / beta))'

    t = parse('(a / alpha :mod-of (b / beta))')
    canonicalize_roles(t, amr_model)
    assert format(t) == '(a / alpha :domain (b / beta))'


def reify_edges():
    pass


def contract_edges():
    pass


def reify_attributes():
    pass


def indicate_branches():
    pass
