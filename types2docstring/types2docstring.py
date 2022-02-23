from __future__ import annotations

import argparse
import ast
from typing import NamedTuple

from tokenize_rt import Offset
from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src

CLASS_METHOD_VARIABLES = ('self', 'cls')


def _subscript_to_annotation(node: ast.Subscript, tokens: list[Token]) -> str:

    node_offset = Offset(node.lineno, node.col_offset)
    annotation = ''

    for i, token in enumerate(tokens):
        # TODO: Document this code really well since its quite complicated
        if token.offset == node_offset:

            depth = 0
            j = i
            # depth indicates wether we are in a type annotation
            # when reacing ',' and depth == 0, it means that
            # the end of the type annotation is reached and a new
            # argument begins when reacing ')' the arguments are done.
            # : is for return types.
            while depth or tokens[j].src not in ',):':
                if tokens[j].src in '[':
                    depth += 1
                elif tokens[j].src in ']':
                    depth -= 1
                annotation += tokens[j].src
                j += 1

    return annotation


def _is_method(node: ast.FunctionDef) -> bool:

    if hasattr(node, 'parent'):
        parent = getattr(node, 'parent')
        if isinstance(parent, ast.ClassDef):
            return True

    return False


def _node_fully_annotated(node: ast.FunctionDef) -> bool:

    # Checks if there is a type specified for the return value.
    if not isinstance(node.returns, ast.Name):
        return False

    # Checks if all arguments are typed
    for child in ast.walk(node):
        if isinstance(child, ast.arg) and child.annotation is None:
            # Allows self and cls to be untyped for methods
            if _is_method(node) and child.arg in CLASS_METHOD_VARIABLES:
                continue

            return False

    return True


class FunctionTypes(NamedTuple):
    args: list[tuple[str, str | None]]
    returns: str


def _get_args_and_types(node: ast.FunctionDef) -> FunctionTypes:

    assert isinstance(node.returns, ast.Name)

    arg_annotations: list[tuple[str, str | None]] = []
    for child in ast.walk(node):

        if isinstance(child, ast.arg):

            if _is_method(node) and child.arg in CLASS_METHOD_VARIABLES:
                arg_annotations.append((child.arg, None))
            else:
                arg_annotations.append(
                    (child.arg, child.annotation.id),  # type: ignore
                )

    return FunctionTypes(args=arg_annotations, returns=node.returns.id)


# TODO: Add option for docstring type
def _generate_docstring(fn_types: FunctionTypes, indent='') -> str:

    # XXX: Improve the way this docstring is generated!
    docstring = [
        '', f"{indent or ''}'''",
        f'{indent}[function description]', '\n',
    ]

    for arg in fn_types.args:
        # Only self is allowed to have no type annotation.
        # Self is not documented, so it has to be skipped here.
        if all(arg):
            docstring.append(
                f'{indent}:param {arg[0]}: [{arg[0]} description]',
            )
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

        for child in ast.iter_child_nodes(node):
            setattr(child, 'parent', node)

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

            # Assuming that we are at the end of the function
            # declaration (see code above), the next INDENT token
            # should give the indentation level of the function
            k = j
            while not tokens[k].name == 'INDENT':
                k += 1

            indent = tokens[k].src
            docstring = _generate_docstring(found[token.offset], indent=indent)
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
