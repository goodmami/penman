
from penman.model import Model
from penman.models.amr import model as amr_model
from penman.codec import PENMANCodec
from penman.transform import (
    canonicalize_roles,
    reify_edges,
    dereify_edges,
    reify_attributes,
    indicate_branches,
)


def_model = Model()
def_codec = PENMANCodec(model=def_model)
amr_codec = PENMANCodec(model=amr_model)


def make_norm(func, model):

    def norm(x):
        return func(x, model)

    return norm


def make_form(func):

    def form(x):
        return func(x, indent=None)

    return form


def test_canonicalize_roles_default_codec():
    parse = def_codec.parse
    norm = make_norm(canonicalize_roles, def_model)
    form = make_form(def_codec.format)

    t = norm(parse('(a / alpha :ARG1 (b / beta))'))
    assert form(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :ARG1-of-of (b / beta))'))
    assert form(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :mod-of (b / beta))'))
    assert form(t) == '(a / alpha :mod-of (b / beta))'


def test_canonicalize_roles_amr_codec():
    parse = amr_codec.parse
    norm = make_norm(canonicalize_roles, amr_model)
    form = make_form(amr_codec.format)

    t = norm(parse('(a / alpha :ARG1 (b / beta))'))
    assert form(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :ARG1-of-of (b / beta))'))
    assert form(t) == '(a / alpha :ARG1 (b / beta))'

    t = norm(parse('(a / alpha :mod-of (b / beta))'))
    assert form(t) == '(a / alpha :domain (b / beta))'

    t = norm(parse('(a / alpha :mod-of~1 (b / beta))'))
    assert form(t) == '(a / alpha :domain~1 (b / beta))'


def test_reify_edges_default_codec():
    decode = def_codec.decode
    norm = make_norm(reify_edges, def_model)
    form = make_form(def_codec.encode)

    g = norm(decode('(a / alpha :mod 5)'))
    assert form(g) == '(a / alpha :mod 5)'

    g = norm(decode('(a / alpha :mod-of (b / beta))'))
    assert form(g) == '(a / alpha :mod-of (b / beta))'


def test_reify_edges_amr_codec():
    decode = amr_codec.decode
    norm = make_norm(reify_edges, amr_model)
    form = make_form(amr_codec.encode)

    g = norm(decode('(a / alpha :mod 5)'))
    assert form(g) == '(a / alpha :ARG1-of (_ / have-mod-91 :ARG2 5))'

    g = norm(decode('(a / alpha :mod-of (b / beta))'))
    assert form(g) == '(a / alpha :ARG2-of (_ / have-mod-91 :ARG1 (b / beta)))'

    g = norm(decode('(a / alpha :mod-of (b / beta :polarity -))'))
    assert form(g) == (
        '(a / alpha :ARG2-of (_ / have-mod-91 '
        ':ARG1 (b / beta :ARG1-of (_2 / have-polarity-91 :ARG2 -))))')

    g = norm(decode('(a / alpha :mod-of~1 (b / beta~2 :polarity -))'))
    assert form(g) == (
        '(a / alpha :ARG2-of (_ / have-mod-91~1 '
        ':ARG1 (b / beta~2 :ARG1-of (_2 / have-polarity-91 :ARG2 -))))')


def test_dereify_edges_default_codec():
    decode = def_codec.decode
    norm = make_norm(dereify_edges, def_model)
    form = make_form(def_codec.encode)

    g = norm(decode('(a / alpha :ARG1-of (_ / have-mod-91'
                    '                       :ARG2 (b / beta)))'))
    assert form(g) == (
        '(a / alpha :ARG1-of (_ / have-mod-91 :ARG2 (b / beta)))')

    g = norm(decode('(a / alpha :ARG2-of (_ / have-mod-91'
                    '                       :ARG1 (b / beta)))'))
    assert form(g) == (
        '(a / alpha :ARG2-of (_ / have-mod-91 :ARG1 (b / beta)))')


def test_dereify_edges_amr_codec():
    decode = amr_codec.decode
    norm = make_norm(dereify_edges, amr_model)
    form = make_form(amr_codec.encode)

    g = norm(decode('(a / alpha :ARG1-of~1 (_ / have-mod-91~2'
                    '                         :ARG2~3 7~4))'))
    assert form(g) == '(a / alpha :mod~2 7~4)'

    g = norm(decode('(a / alpha :ARG1-of~1 (_ / have-mod-91~2'
                    '                       :ARG2~3 (b / beta~4)))'))
    assert form(g) == '(a / alpha :mod~2 (b / beta~4))'

    g = norm(decode('(a / alpha :ARG2-of (_ / have-mod-91'
                    '                       :ARG1 (b / beta)))'))
    assert form(g) == '(a / alpha :mod-of (b / beta))'

    # dereification is blocked because node has additional relations
    g = norm(decode('(a / alpha :ARG1-of (_ / have-mod-91'
                    '                       :ARG2 (b / beta)'
                    '                       :polarity -))'))
    assert form(g) == (
        '(a / alpha :ARG1-of (_ / have-mod-91 :ARG2 (b / beta) :polarity -))')

    g = norm(decode('''
        (a / alpha
            :ARG1-of (b / beta
                        :ARG0 p)
            :ARG1-of (g / gamma
                        :ARG1-of (_ / own-01
                                    :ARG0 (p / pi))))'''))
    assert form(g) == (
        '(a / alpha :ARG1-of (b / beta :ARG0 p)'
        ' :ARG1-of (g / gamma :poss (p / pi)))')

    # Re-enable the following test if we have a way to remove POPs
    # from epidata at the ends of "branches" in the graph
    #
    # g = norm(decode('''
    #     (a / alpha
    #        :ARG0 (b / beta)
    #        :ARG1 (g / gamma
    #                  :ARG1-of (_ / have-quant-91
    #                              :ARG2 4)
    #                  :ARG2-of (_2 / have-part-91
    #                               :ARG1 b))))'''))
    # assert form(g) == (
    #     '(a / alpha :ARG0 (b / beta)'
    #     ' :ARG1 (g / gamma :quant 4 :part-of b))')


def test_reify_attributes():
    decode = def_codec.decode
    norm = reify_attributes
    form = make_form(def_codec.encode)

    g = norm(decode('(a / alpha :mod 5)'))
    assert form(g) == '(a / alpha :mod (_ / 5))'

    g = norm(decode('(a / alpha :mod~1 5~2)'))
    assert form(g) == '(a / alpha :mod~1 (_ / 5~2))'


def test_indicate_branches():
    decode = def_codec.decode
    norm = make_norm(indicate_branches, def_model)
    form = make_form(def_codec.encode)

    g = norm(decode('(a / alpha :mod 5)'))
    assert form(g) == '(a / alpha :mod 5)'

    g = norm(decode('(a / alpha :mod-of (b / beta))'))
    assert form(g) == '(a / alpha :TOP b :mod-of (b / beta))'


def test_issue_35():
    # https://github.com/goodmami/penman/issues/35

    # don't re-encode; these (presumably) bad graphs probably won't
    # round-trip without changes. Changes may be predictable, but I
    # don't want to test and guarantee some particular output

    g = amr_codec.decode('(a / alpha :mod b :mod (b / beta))')
    g = reify_edges(g, amr_model)
    assert g.triples == [
        ('a', ':instance', 'alpha'),
        ('_', ':ARG1', 'a'),
        ('_', ':instance', 'have-mod-91'),
        ('_', ':ARG2', 'b'),
        ('_2', ':ARG1', 'a'),
        ('_2', ':instance', 'have-mod-91'),
        ('_2', ':ARG2', 'b'),
        ('b', ':instance', 'beta')]

    g = amr_codec.decode('(a / alpha :mod 7 :mod 7))')
    g = reify_attributes(g)
    assert g.triples == [
        ('a', ':instance', 'alpha'),
        ('a', ':mod', '_'),
        ('_', ':instance', '7'),
        ('a', ':mod', '_2'),
        ('_2', ':instance', '7')]
