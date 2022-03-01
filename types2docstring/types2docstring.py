from __future__ import annotations

import argparse
import ast
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Union

from tokenize_rt import Offset
from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src

CLASS_METHOD_VARIABLES = ('self', 'cls')


class FunctionTypes(NamedTuple):
    args: list[tuple[str, str | None]]
    returns: str


def _node_to_annotation(
    node: Union[ast.Subscript, ast.BinOp],
    tokens: list[Token],
) -> str:

    node_offset = Offset(node.lineno, node.col_offset)
    annotation = ''

    for i, token in enumerate(tokens):
        if token.offset == node_offset:
            depth = 0
            j = i
            # depth indicates wether we are in a type annotation.
            # When reaching ',' and depth == 0, it means that
            # the end of the type annotation is reached.
            # The `)`indicates that the end of the parameters declaration
            # is reached.
            # `:` is for return types and means that the end of the
            # function declaration is reached.
            # `=` means that there is a default argument, so after the
            # equal there is no type annotation.
            while depth or tokens[j].src not in ',):=':
                if tokens[j].src in '[':
                    depth += 1
                elif tokens[j].src in ']':
                    depth -= 1
                annotation += tokens[j].src
                j += 1

    # The annotation sometimes may include trailing whitespace
    # it is easier to remove it here then change how the
    # annotation is parsed.
    return annotation.strip()


def _is_method(node: ast.FunctionDef) -> bool:

    if hasattr(node, 'parent'):
        parent = getattr(node, 'parent')
        if isinstance(parent, ast.ClassDef):
            return True

    return False


def _is_return_annotated(node: ast.FunctionDef) -> bool:
    return (
        isinstance(node.returns, ast.Name) or
        isinstance(node.returns, ast.Subscript)
    )


def _node_fully_annotated(node: ast.FunctionDef) -> bool:

    if not _is_return_annotated(node):
        return False

    for child in ast.walk(node):
        if isinstance(child, ast.arg) and child.annotation is None:
            # Allows self and cls to be untyped for methods
            if _is_method(node) and child.arg in CLASS_METHOD_VARIABLES:
                continue

            return False

    return True


def _get_args_and_types(
    node: ast.FunctionDef,
    tokens: list[Token],
) -> FunctionTypes:

    assert _is_return_annotated(node)

    arg_annotations: list[tuple[str, str | None]] = []
    for child in ast.walk(node):

        if isinstance(child, ast.arg):
            if _is_method(node) and child.arg in CLASS_METHOD_VARIABLES:
                # `self` and `cls` are not typed..
                arg_annotations.append((child.arg, None))
            elif (
                isinstance(child.annotation, ast.Subscript) or
                isinstance(child.annotation, ast.BinOp)
            ):
                arg_annotations.append(
                    (
                        child.arg,
                        _node_to_annotation(
                            child.annotation,
                            tokens,
                        ),
                    ),
                )
            else:
                assert child.annotation is not None, (
                    'annotation cannot be None'
                )
                assert hasattr(child.annotation, 'id'), 'annotation needs id'
                arg_annotations.append(
                    (child.arg, getattr(child.annotation, 'id')),
                )

    return_type = ''
    if isinstance(node.returns, ast.Subscript):
        return_type = _node_to_annotation(node.returns, tokens)
    else:
        assert node.returns is not None and hasattr(node.returns, 'id')
        return_type = getattr(node.returns, 'id')

    return FunctionTypes(
        args=arg_annotations,
        returns=return_type,
    )


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
    tokens = src_to_tokens(contents)

    found: dict[Offset, FunctionTypes] = {}

    for node in ast.walk(tree):

        for child in ast.iter_child_nodes(node):
            setattr(child, 'parent', node)

        if (
            isinstance(node, ast.FunctionDef) and
            _node_fully_annotated(node) and
            ast.get_docstring(node) is None
        ):
            ft = _get_args_and_types(node, tokens)
            found[Offset(node.lineno, node.col_offset)] = ft

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


def _main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)

    ret = 0

    for filename in args.filenames:
        ret |= _rewrite_file(filename)

    return ret
