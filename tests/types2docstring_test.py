import ast

import pytest
from tokenize_rt import src_to_tokens

from types2docstring.types2docstring import _generate_docstring
from types2docstring.types2docstring import _get_args_and_types
from types2docstring.types2docstring import _is_method
from types2docstring.types2docstring import _node_fully_annotated
from types2docstring.types2docstring import _node_to_annotation
from types2docstring.types2docstring import FunctionTypes


def _create_nodes(source):

    tree = ast.parse(source)

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            setattr(child, 'parent', node)

    return tree


def test_node_to_annotation():
    source = """\\
    def t(x: list[set[int]]) -> list[set[Union[int, str]]]:
        return x
    """
    # TODO: Simplify these tests
    tree = ast.parse(source)
    tokens = src_to_tokens(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):

            # Test for the arguments
            for arg in node.args.args:
                if hasattr(arg, 'annotation'):
                    if isinstance(getattr(arg, 'annotation'), ast.Subscript):
                        a = _node_to_annotation(
                            getattr(arg, 'annotation'), tokens,
                        )
                        assert a == 'list[set[int]]'
                else:  # pragma: nocover
                    assert False

            # Test the return annotation
            if isinstance(node.returns, ast.Subscript):
                a = _node_to_annotation(node.returns, tokens)
                assert a == 'list[set[Union[int, str]]]'
            else:  # pragma: nocover
                assert False


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


@pytest.mark.parametrize(
    'source, expected', [
        (
            'class C:\n'
            '   def t(self, x: int) -> int:\n'
            '       return x\n',
            FunctionTypes([('self', None), ('x', 'int')], 'int'),
        ),
        (
            'class C:\n'
            '   @classmethod\n'
            '   def t(cls, x:int) -> int:\n'
            '       return x\n',
            FunctionTypes([('cls', None), ('x', 'int')], 'int'),
        ),
        (
            'def f(x: list[set[int]]) -> list[list[int]]:\n'
            '   return x\n',
            FunctionTypes([('x', 'list[set[int]]')], 'list[list[int]]'),
        ),
        (
            'def f(x: Optional[str] = None) -> str:\n'
            '   return x\n',
            FunctionTypes([('x', 'Optional[str]')], 'str'),
        ),
        (
            'def f(x: str | None = None) -> str:\n'
            '   return x\n',
            FunctionTypes([('x', 'str | None')], 'str'),
        ),
    ],
)
def test_get_args_and_types(source, expected):

    node = _create_nodes(source)
    tokens = src_to_tokens(source)

    for child in ast.walk(node):
        if isinstance(child, ast.FunctionDef):
            types = _get_args_and_types(child, tokens)
            assert types == expected


@pytest.mark.parametrize(
    'fn_types, expected', [
        (
            FunctionTypes([('x', 'int')], 'int'),
            "\n'''\n"
            '[function description]\n'
            '\n'
            '\n:param x: [x description]\n'
            ':type x: int\n'
            '\n'
            '\n:returns: [return description]\n'
            ':rtype: int\n'
            "'''\n",
        ),
        (
            FunctionTypes([('x', 'list[list[int]]')], 'int'),
            "\n'''\n"
            '[function description]\n'
            '\n'
            '\n:param x: [x description]\n'
            ':type x: list[list[int]]\n'
            '\n'
            '\n:returns: [return description]\n'
            ':rtype: int\n'
            "'''\n",
        ),
        (
            FunctionTypes(
                [
                    ('x', 'tuple[int, int, str]'),
                    ('y', 'Union[set[str], int]'),
                ], 'int',
            ),
            "\n'''\n"
            '[function description]\n'
            '\n'
            '\n:param x: [x description]\n'
            ':type x: tuple[int, int, str]\n'
            ':param y: [y description]\n'
            ':type y: Union[set[str], int]\n'
            '\n'
            '\n:returns: [return description]\n'
            ':rtype: int\n'
            "'''\n",
        ),
    ],
)
def test_generate_docstring(fn_types, expected):

    assert _generate_docstring(fn_types) == expected
