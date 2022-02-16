import ast

from types2docstring.types2docstring import _is_method


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

    source = """class C:

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
