
import pytest

from penman import tree


@pytest.fixture
def empty_node():
    return ('a')


@pytest.fixture
def simple_node():
    return ('a', [('/', 'alpha')])


@pytest.fixture
def one_arg_node():
    return ('a', [('/', 'alpha'),
                  (':ARG0', ('b', [('/', 'beta')]))])


@pytest.fixture
def reentrant():
    return ('a', [('/', 'alpha'),
                  (':ARG0', ('b', [('/', 'beta')])),
                  (':ARG1', ('g', [('/', 'gamma'),
                                   (':ARG0', 'b')]))])


@pytest.fixture
def var_instance():
    return ('a', [('/', 'alpha'),
                  (':ARG0', ('b', [('/', 'b')]))])


class TestTree:
    def test__init__(self, empty_node, simple_node):
        with pytest.raises(TypeError):
            tree.Tree()

        t = tree.Tree(empty_node)
        assert t.node == empty_node
        assert t.metadata == {}

        t = tree.Tree(simple_node, metadata={'snt': 'Alpha.'})
        assert t.node == simple_node
        assert t.metadata == {'snt': 'Alpha.'}

    def test_nodes(self, one_arg_node, reentrant):
        t = tree.Tree(one_arg_node)
        assert t.nodes() == [one_arg_node, ('b', [('/', 'beta')])]

        t = tree.Tree(reentrant)
        assert t.nodes() == [reentrant,
                             ('b', [('/', 'beta')]),
                             ('g', [('/', 'gamma'), (':ARG0', 'b')])]

    def test_walk(self, one_arg_node, reentrant):
        t = tree.Tree(one_arg_node)
        assert list(t.walk()) == [
            ((0,), ('/', 'alpha')),
            ((1,), (':ARG0', ('b', [('/', 'beta')]))),
            ((1, 0), ('/', 'beta')),
        ]

        t = tree.Tree(reentrant)
        assert list(t.walk()) == [
            ((0,), ('/', 'alpha')),
            ((1,), (':ARG0', ('b', [('/', 'beta')]))),
            ((1, 0), ('/', 'beta')),
            ((2,), (':ARG1', ('g', [('/', 'gamma'),
                                    (':ARG0', 'b')]))),
            ((2, 0), ('/', 'gamma')),
            ((2, 1), (':ARG0', 'b')),
        ]

        t = tree.Tree(('a', [('/', 'alpha'),
                             (':polarity', '-'),
                             (':ARG0', ('b', [('/', 'beta')]))]))
        assert list(t.walk()) == [
            ((0,), ('/', 'alpha')),
            ((1,), (':polarity', '-')),
            ((2,), (':ARG0', ('b', [('/', 'beta')]))),
            ((2, 0), ('/', 'beta')),
        ]

    def test_reset_variables(self, one_arg_node, reentrant, var_instance):

        def _vars(t):
            return [v for v, _ in t.nodes()]

        t = tree.Tree(one_arg_node)
        assert _vars(t) == ['a', 'b']

        t.reset_variables(fmt='a{i}')
        assert _vars(t) == ['a0', 'a1']

        t.reset_variables(fmt='a{j}')
        assert _vars(t) == ['a', 'a2']

        t.reset_variables()
        assert _vars(t) == ['a', 'b']

        t = tree.Tree(reentrant)
        assert _vars(t) == ['a', 'b', 'g']

        t.reset_variables(fmt='a{i}')
        assert _vars(t) == ['a0', 'a1', 'a2']
        assert t == (
            'a0', [('/', 'alpha'),
                   (':ARG0', ('a1', [('/', 'beta')])),
                   (':ARG1', ('a2', [('/', 'gamma'),
                                     (':ARG0', 'a1')]))])

        t.reset_variables()
        assert _vars(t) == ['a', 'b', 'g']

        t = tree.Tree(var_instance)
        assert _vars(t) == ['a', 'b']

        t.reset_variables(fmt='a{i}')
        assert _vars(t) == ['a0', 'a1']
        assert t == (
            'a0', [('/', 'alpha'),
                   (':ARG0', ('a1', [('/', 'b')]))])

        t.reset_variables()
        assert _vars(t) == ['a', 'b']


def test_is_atomic():
    assert tree.is_atomic('a')
    assert tree.is_atomic(None)
    assert tree.is_atomic(3.14)
    assert not tree.is_atomic(('a', [('/', 'alpha')]))


def test_default_variable_prefix():
    assert tree._default_variable_prefix('Alphabet') == 'a'
    assert tree._default_variable_prefix('chase-01') == 'c'
    assert tree._default_variable_prefix('"string"') == 's'
    assert tree._default_variable_prefix('_predicate_n_1"') == 'p'
    assert tree._default_variable_prefix(1) == '_'
    assert tree._default_variable_prefix(None) == '_'
    assert tree._default_variable_prefix('') == '_'
