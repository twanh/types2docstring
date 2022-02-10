from __future__ import annotations

import argparse
import ast

from tokenize_rt import Offset


def _node_fully_annotated(node: ast.FunctionDef) -> bool:

    # Checks if there is a type specified for the return value.
    if not isinstance(node.returns, ast.Name):
        return False

    # Checks if all arguments are typed
    for child in ast.walk(node):
        if isinstance(child, ast.arg) and child.annotation is None:
            return False

    return True


def _rewrite_file(filename: str) -> int:

    with open(filename, encoding='UTF-8') as file:
        contents = file.read()

    tree = ast.parse(contents)

    found_offsets: set[Offset] = set()

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef) and
            _node_fully_annotated(node) and
            ast.get_docstring(node) is None
        ):
            found_offsets.add(Offset(node.lineno, node.col_offset))

    return 0


def _main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args()

    ret = 0

    for filename in args.filenames:
        ret |= _rewrite_file(filename)

    return ret
