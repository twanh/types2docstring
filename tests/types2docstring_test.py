import ast

import pytest

from types2docstring.types2docstring import _is_method
from types2docstring.types2docstring import _node_fully_annotated


def _create_nodes(source):

    tree = ast.parse(source)

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, 'parent', node)

    return tree


def test_is_method_no_parent_attr():

    fn = """def f(x: int) -> int:
        return x*x
    """
    node = ast.parse(fn)

    assert isinstance(node.body[0], ast.FunctionDef)
    assert _is_method(node.body[0]) is False


def test_is_method_with_parent_no_method():

    fn = """def f(x: int) -> int:
        return x*x
    """
    node = ast.parse(fn)
    setattr(node.body[0], 'parent', node)
    assert isinstance(node.body[0], ast.FunctionDef)
    assert hasattr(node.body[0], 'parent')
    assert _is_method(node.body[0]) is False


def test_is_method():

    source = """\\
    class C:
        def test(self, x: int) -> int:
            return x*x

        @classmethod
        def test2(cls, x:int) -> int:
            return x*x
    """

    tree = ast.parse(source)

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, 'parent', node)

    assert isinstance(tree.body[0], ast.ClassDef)
    fns = tree.body[0].body

    assert isinstance(fns[0], ast.FunctionDef)
    assert _is_method(fns[0]) is True
    assert isinstance(fns[1], ast.FunctionDef)
    assert _is_method(fns[1]) is True


@pytest.mark.parametrize(
    'source,expected', [
        (
            'def t(x: int, y:int) -> int:\n'
            '   return x*y\n',
            True,
        ),
        (
            'def t(x: int, y: int):\n'
            '   return x*y\n',
            False,
        ),
        (
            'def t(x, y):\n'
            '   return x*y\n', False,
        ),
        (
            'def t(x, y) -> int:\n'
            '   return x*y\n',
            False,
        ),
        (
            'def t(x: list[int]) -> int:\n'
            '   return sum(x)\n',
            True,
        ),
        (
            'def t(x: list[set[int]]) -> list[set[int]]:'
            '   return x',
            True,
        ),
    ],
)
def test_node_fully_annotated(source, expected):

    nodes = _create_nodes(source)
    for node in ast.walk(nodes):
        if isinstance(node, ast.FunctionDef):
            assert _node_fully_annotated(node) is expected


@pytest.mark.parametrize(
    'source, expected', [
        (
            'class C:\n'
            '   def t(self, x: int) -> int:\n'
            '       return x\n',
            True,
        ),
        (
            'class C:\n'
            '   @classmethod\n'
            '   def t(cls, x:int) -> int:\n'
            '       return x\n',
            True,
        ),
        (
            'class C:\n'
            '   def t(self, x):\n'
            '       return  x\n',
            False,
        ),
        (
            'class C:\n'
            '   @classmethod\n'
            '   def t(cls, x):\n'
            '       return  x\n',
            False,
        ),
    ],
)
def test_node_fully_annotated_methods(source, expected):
    nodes = _create_nodes(source)
    for node in ast.walk(nodes):
        if isinstance(node, ast.FunctionDef):
            assert _node_fully_annotated(node) is expected
