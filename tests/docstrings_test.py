import pytest

from types2docstring._docstrings._google import generate_google_docstring
from types2docstring._docstrings._rst import generate_rst_docstring
from types2docstring._helpers import FunctionTypes

# RST DOCSTRING test


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
def test_generate_rst_docstring(fn_types, expected):
    assert generate_rst_docstring(fn_types, '') == expected


# Google docstring tests

@pytest.mark.parametrize(
    'fn_types, expected', [
        (
            FunctionTypes([('x', 'int')], 'int'),
            "\n'''"
            '[function description]\n'
            '\n'
            'Args:'
            '\n\tx (int): [argument description]'
            '\n'
            '\nReturns:'
            '\n\tint: [return description]'
            '\n'
            "'''\n",
        ),
    ],
)
def test_generate_google_docstring(fn_types, expected):
    assert generate_google_docstring(fn_types, '') == expected
