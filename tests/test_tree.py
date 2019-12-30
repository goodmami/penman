
import pytest

from penman import tree


@pytest.fixture
def empty_node():
    return ('a', [])


@pytest.fixture
def simple_node():
    return ('a', [('/', 'alpha', [])])


@pytest.fixture
def one_arg_node():
    return ('a', [('/', 'alpha', []),
                  (':ARG0', ('b', [('/', 'beta', [])]), [])])


@pytest.fixture
def reentrant():
    return ('a', [('/', 'alpha', []),
                  (':ARG0', ('b', [('/', 'beta', [])]), []),
                  (':ARG1', ('g', [('/', 'gamma', []),
                                   (':ARG0', 'b', [])]), [])])


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
        assert t.nodes() == [one_arg_node, ('b', [('/', 'beta', [])])]

        t = tree.Tree(reentrant)
        assert t.nodes() == [reentrant,
                             ('b', [('/', 'beta', [])]),
                             ('g', [('/', 'gamma', []), (':ARG0', 'b', [])])]


def test_is_atomic():
    assert tree.is_atomic('a')
    assert tree.is_atomic(None)
    assert tree.is_atomic(3.14)
    assert not tree.is_atomic(('a', [('/', 'alpha', [])]))
