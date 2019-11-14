
import pytest

from penman.exceptions import ModelError
from penman.model import Model



class TestModel:
    def test__init__(self, mini_amr):
        m = Model()
        assert len(m.roles) == 0
        m = Model(roles=mini_amr['roles'])
        assert len(m.roles) == 7

    def test_from_dict(self, mini_amr):
        assert Model.from_dict(mini_amr) == Model(
            roles=mini_amr['roles'],
            normalizations=mini_amr['normalizations'],
            reifications=mini_amr['reifications'])

    def test_has_role(self, mini_amr):
        m = Model()
        assert not m.has_role('')
        assert m.has_role(m.nodetype_role)
        assert not m.has_role(':ARG0')
        assert not m.has_role(':ARG0-of')
        m = Model.from_dict(mini_amr)
        assert not m.has_role('')
        assert m.has_role(m.nodetype_role)
        assert m.has_role(':ARG0')
        assert m.has_role(':ARG0-of')
        assert m.has_role(':mod')
        assert m.has_role(':mod-of')
        assert not m.has_role(':consist')
        assert m.has_role(':consist-of')
        assert m.has_role(':consist-of-of')
        assert not m.has_role(':fake')
        assert m.has_role(':op1')
        assert m.has_role(':op10')
        assert m.has_role(':op9999')
        assert not m.has_role(':op[0-9]+')

    def test_is_role_inverted(self, mini_amr):
        m = Model()
        assert m.is_role_inverted(':ARG0-of')
        assert m.is_role_inverted(':-of')
        assert not m.is_role_inverted(':ARG0')
        assert not m.is_role_inverted(':')
        assert m.is_role_inverted(':consist-of')
        # # without :
        # assert m.is_role_inverted('ARG0-of')
        # assert not m.is_role_inverted('ARG0')

        m = Model.from_dict(mini_amr)
        assert m.is_role_inverted(':mod-of')
        assert m.is_role_inverted(':domain-of')
        assert not m.is_role_inverted(':mod')
        assert not m.is_role_inverted(':domain')
        assert m.is_role_inverted(':consist-of-of')
        assert not m.is_role_inverted(':consist-of')
        # # without :
        # assert m.is_role_inverted('mod-of')
        # assert not m.is_role_inverted('mod')
        # assert not m.is_role_inverted('consist-of')

    def test_invert_role(self, mini_amr):
        m = Model()
        assert m.invert_role(':ARG0')       == ':ARG0-of'
        assert m.invert_role(':ARG0-of')    == ':ARG0'
        assert m.invert_role(':consist-of') == ':consist'
        assert m.invert_role(':mod')        == ':mod-of'
        assert m.invert_role(':domain')     == ':domain-of'
        # # without :
        # assert m.invert_role('ARG0')       == 'ARG0-of'
        # assert m.invert_role('ARG0-of')    == 'ARG0'

        m = Model.from_dict(mini_amr)
        assert m.invert_role(':ARG0')       == ':ARG0-of'
        assert m.invert_role(':ARG0-of')    == ':ARG0'
        assert m.invert_role(':consist-of') == ':consist-of-of'
        assert m.invert_role(':mod')        == ':mod-of'
        assert m.invert_role(':domain')     == ':domain-of'
        # # without :
        # assert m.invert_role('mod')        == 'domain'
        # assert m.invert_role('domain')     == 'mod'

    def test_invert(self, mini_amr):
        m = Model()
        assert m.invert(('a', ':ARG0', 'b'))       == ('b', ':ARG0-of', 'a')
        assert m.invert(('a', ':ARG0-of', 'b'))    == ('b', ':ARG0', 'a')
        assert m.invert(('a', ':consist-of', 'b')) == ('b', ':consist', 'a')
        assert m.invert(('a', ':mod', 'b'))        == ('b', ':mod-of', 'a')
        assert m.invert(('a', ':domain', 'b'))     == ('b', ':domain-of', 'a')
        # # without :
        # assert m.invert(('a', 'ARG0', 'b'))        == ('b', 'ARG0-of', 'a')
        # assert m.invert(('a', 'ARG0-of', 'b'))     == ('b', 'ARG0', 'a')

        m = Model.from_dict(mini_amr)
        assert m.invert(('a', ':ARG0', 'b'))       == ('b', ':ARG0-of', 'a')
        assert m.invert(('a', ':ARG0-of', 'b'))    == ('b', ':ARG0', 'a')
        assert m.invert(('a', ':consist-of', 'b')) == ('b', ':consist-of-of', 'a')
        assert m.invert(('a', ':mod', 'b'))        == ('b', ':mod-of', 'a')
        assert m.invert(('a', ':domain', 'b'))     == ('b', ':domain-of', 'a')
        # # without :
        # assert m.invert(('a', 'mod', 'b'))         == ('b', 'domain', 'a')
        # assert m.invert(('a', 'domain', 'b'))      == ('b', 'mod', 'a')


    def test_deinvert(self, mini_amr):
        m = Model()
        assert m.deinvert(('a', ':ARG0', 'b'))       == ('a', ':ARG0', 'b')
        assert m.deinvert(('a', ':ARG0-of', 'b'))    == ('b', ':ARG0', 'a')
        assert m.deinvert(('a', ':consist-of', 'b')) == ('b', ':consist', 'a')
        assert m.deinvert(('a', ':mod', 'b'))        == ('a', ':mod', 'b')
        assert m.deinvert(('a', ':domain', 'b'))     == ('a', ':domain', 'b')
        # # without :
        # assert m.deinvert(('a', 'ARG0', 'b'))        == ('a', 'ARG0', 'b')
        # assert m.deinvert(('a', 'ARG0-of', 'b'))     == ('b', 'ARG0', 'a')

        m = Model.from_dict(mini_amr)
        assert m.deinvert(('a', ':ARG0', 'b'))       == ('a', ':ARG0', 'b')
        assert m.deinvert(('a', ':ARG0-of', 'b'))    == ('b', ':ARG0', 'a')
        assert m.deinvert(('a', ':consist-of', 'b')) == ('a', ':consist-of', 'b')
        assert m.deinvert(('a', ':mod', 'b'))        == ('a', ':mod', 'b')
        assert m.deinvert(('a', ':domain', 'b'))     == ('a', ':domain', 'b')
        # # without :
        # assert m.deinvert(('a', 'ARG0-of', 'b'))     == ('b', 'ARG0', 'a')
        # assert m.deinvert(('a', 'consist-of', 'b'))  == ('a', 'consist-of', 'b')

    def test_canonicalize_role(self, mini_amr):
        m = Model()
        assert m.canonicalize_role(':ARG0')          == ':ARG0'
        assert m.canonicalize_role(':ARG0-of')       == ':ARG0-of'
        assert m.canonicalize_role(':ARG0-of-of')    == ':ARG0'
        assert m.canonicalize_role(':consist')       == ':consist'
        assert m.canonicalize_role(':consist-of')    == ':consist-of'
        assert m.canonicalize_role(':consist-of-of') == ':consist'
        assert m.canonicalize_role(':mod')           == ':mod'
        assert m.canonicalize_role(':mod-of')        == ':mod-of'
        assert m.canonicalize_role(':domain')        == ':domain'
        assert m.canonicalize_role(':domain-of')     == ':domain-of'
        # without :
        assert m.canonicalize_role('ARG0')           == ':ARG0'
        assert m.canonicalize_role('ARG0-of')        == ':ARG0-of'
        assert m.canonicalize_role('ARG0-of-of')     == ':ARG0'

        m = Model.from_dict(mini_amr)
        assert m.canonicalize_role(':ARG0')          == ':ARG0'
        assert m.canonicalize_role(':ARG0-of')       == ':ARG0-of'
        assert m.canonicalize_role(':ARG0-of-of')    == ':ARG0'
        assert m.canonicalize_role(':consist')       == ':consist-of-of'
        assert m.canonicalize_role(':consist-of')    == ':consist-of'
        assert m.canonicalize_role(':consist-of-of') == ':consist-of-of'
        assert m.canonicalize_role(':mod')           == ':mod'
        assert m.canonicalize_role(':mod-of')        == ':domain'
        assert m.canonicalize_role(':domain')        == ':domain'
        assert m.canonicalize_role(':domain-of')     == ':mod'
        # without :
        assert m.canonicalize_role('consist')        == ':consist-of-of'
        assert m.canonicalize_role('consist-of')     == ':consist-of'
        assert m.canonicalize_role('consist-of-of')  == ':consist-of-of'

    def test_canonicalize(self, mini_amr):
        m = Model()
        assert m.canonicalize(('a', ':ARG0', 'b'))          == ('a', ':ARG0', 'b')
        assert m.canonicalize(('a', ':ARG0-of', 'b'))       == ('a', ':ARG0-of', 'b')
        assert m.canonicalize(('a', ':ARG0-of-of', 'b'))    == ('a', ':ARG0', 'b')
        assert m.canonicalize(('a', ':consist', 'b'))       == ('a', ':consist', 'b')
        assert m.canonicalize(('a', ':consist-of', 'b'))    == ('a', ':consist-of', 'b')
        assert m.canonicalize(('a', ':consist-of-of', 'b')) == ('a', ':consist', 'b')
        assert m.canonicalize(('a', ':mod', 'b'))           == ('a', ':mod', 'b')
        assert m.canonicalize(('a', ':mod-of', 'b'))        == ('a', ':mod-of', 'b')
        assert m.canonicalize(('a', ':domain', 'b'))        == ('a', ':domain', 'b')
        assert m.canonicalize(('a', ':domain-of', 'b'))     == ('a', ':domain-of', 'b')
        # without :
        assert m.canonicalize(('a', 'ARG0', 'b'))           == ('a', ':ARG0', 'b')
        assert m.canonicalize(('a', 'ARG0-of', 'b'))        == ('a', ':ARG0-of', 'b')
        assert m.canonicalize(('a', 'ARG0-of-of', 'b'))     == ('a', ':ARG0', 'b')

        m = Model.from_dict(mini_amr)
        assert m.canonicalize(('a', ':ARG0', 'b'))          == ('a', ':ARG0', 'b')
        assert m.canonicalize(('a', ':ARG0-of', 'b'))       == ('a', ':ARG0-of', 'b')
        assert m.canonicalize(('a', ':ARG0-of-of', 'b'))    == ('a', ':ARG0', 'b')
        assert m.canonicalize(('a', ':consist', 'b'))       == ('a', ':consist-of-of', 'b')
        assert m.canonicalize(('a', ':consist-of', 'b'))    == ('a', ':consist-of', 'b')
        assert m.canonicalize(('a', ':consist-of-of', 'b')) == ('a', ':consist-of-of', 'b')
        assert m.canonicalize(('a', ':mod', 'b'))           == ('a', ':mod', 'b')
        assert m.canonicalize(('a', ':mod-of', 'b'))        == ('a', ':domain', 'b')
        assert m.canonicalize(('a', ':domain', 'b'))        == ('a', ':domain', 'b')
        assert m.canonicalize(('a', ':domain-of', 'b'))     == ('a', ':mod', 'b')
        # without :
        assert m.canonicalize(('a', 'consist', 'b'))        == ('a', ':consist-of-of', 'b')
        assert m.canonicalize(('a', 'consist-of', 'b'))     == ('a', ':consist-of', 'b')
        assert m.canonicalize(('a', 'consist-of-of', 'b'))  == ('a', ':consist-of-of', 'b')

    def test_is_reifiable(self, mini_amr):
        m = Model()
        assert not m.is_reifiable(('a', ':ARG0', 'b'))
        assert not m.is_reifiable(('a', ':accompanier', 'b'))
        assert not m.is_reifiable(('a', ':domain', 'b'))
        assert not m.is_reifiable(('a', ':mod', 'b'))
        m = Model.from_dict(mini_amr)
        assert not m.is_reifiable(('a', ':ARG0', 'b'))
        assert m.is_reifiable(('a', ':accompanier', 'b'))
        assert not m.is_reifiable(('a', ':domain', 'b'))
        assert m.is_reifiable(('a', ':mod', 'b'))

    def test_reify(self, mini_amr):
        m = Model()
        with pytest.raises(ModelError):
            m.reify(('a', ':ARG0', 'b'))
        with pytest.raises(ModelError):
            m.reify(('a', ':accompanier', 'b'))
        with pytest.raises(ModelError):
            m.reify(('a', ':domain', 'b'))
        with pytest.raises(ModelError):
            m.reify(('a', ':mod', 'b'))
        m = Model.from_dict(mini_amr)
        with pytest.raises(ModelError):
            m.reify(('a', ':ARG0', 'b'))
        assert m.reify(('a', ':accompanier', 'b')) == (
            ('a', ':ARG0-of', '_'),
            ('_', ':instance', 'accompany-01'),
            ('_', ':ARG1', 'b'))
        with pytest.raises(ModelError):
            assert m.reify(('a', ':domain', 'b'))
        assert m.reify(('a', ':mod', 'b')) == (
            ('a', ':ARG1-of', '_'),
            ('_', ':instance', 'have-mod-91'),
            ('_', ':ARG2', 'b'))
        # ensure unique ids if variables is specified
        assert m.reify(('a', ':mod', 'b'), variables={'a', 'b', '_'}) == (
            ('a', ':ARG1-of', '_2'),
            ('_2', ':instance', 'have-mod-91'),
            ('_2', ':ARG2', 'b'))
