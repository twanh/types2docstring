from __future__ import annotations

import argparse
import ast
from typing import NamedTuple

from tokenize_rt import Offset
from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import tokens_to_src


def _node_fully_annotated(node: ast.FunctionDef) -> bool:

    # Checks if there is a type specified for the return value.
    if not isinstance(node.returns, ast.Name):
        return False

    # Checks if all arguments are typed
    for child in ast.walk(node):
        if isinstance(child, ast.arg) and child.annotation is None:
            return False

    return True


class FunctionTypes(NamedTuple):
    # TODO: Is this the best way to represent this?
    args: list[tuple[str, str]]
    returns: str


def _get_args_and_types(node: ast.FunctionDef) -> FunctionTypes:

    assert isinstance(node.returns, ast.Name)

    arg_annotations = []
    for child in ast.walk(node):
        if isinstance(child, ast.arg):
            assert child.annotation
            arg_annotations.append(
                (child.arg, child.annotation.id),  # type: ignore
            )

    return FunctionTypes(args=arg_annotations, returns=node.returns.id)


# TODO: Add option for docstring type
def _generate_docstring(fn_types: FunctionTypes, indent='') -> str:

    docstring = [
        '', f"{indent or ''}'''",
        f'{indent}[function description]', '\n',
    ]

    for arg in fn_types.args:
        docstring.append(f'{indent}:param {arg[0]}: [{arg[0]} desciption]')
        docstring.append(f'{indent}:type {arg[0]}: {arg[1]}')

    docstring.append('\n')
    docstring.append(f'{indent}:returns: [return description]')
    docstring.append(f'{indent}:rtype: {fn_types.returns}')

    docstring.append(f"{indent or ''}'''\n")

    return '\n'.join(docstring)


def _rewrite_file(filename: str) -> int:

    with open(filename, encoding='UTF-8') as file:
        contents = file.read()

    tree = ast.parse(contents)

    found: dict[Offset, FunctionTypes] = {}

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef) and
            _node_fully_annotated(node) and
            ast.get_docstring(node) is None
        ):
            ft = _get_args_and_types(node)
            found[Offset(node.lineno, node.col_offset)] = ft

    tokens = src_to_tokens(contents)
    for i, token in reversed_enumerate(tokens):
        if token.src and token.offset in found:
            depth = 0
            j = i
            while depth or tokens[j].src != ':':
                if tokens[j].src in '({[':
                    depth += 1
                elif tokens[j].src in ')]}':
                    depth -= 1
                j += 1

            # TODO: Get the actual (correct) indentation
            docstring = _generate_docstring(found[token.offset], indent='    ')
            tokens[j] = tokens[j]._replace(src=f':{docstring}')

    new_contents = tokens_to_src(tokens)
    with open(filename, 'w') as f:
        f.write(new_contents)

    return new_contents != contents


def _main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args()

    ret = 0

    for filename in args.filenames:
        ret |= _rewrite_file(filename)

    return ret
