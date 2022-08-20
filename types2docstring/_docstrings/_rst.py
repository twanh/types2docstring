from types2docstring._helpers import FunctionTypes
from types2docstring._helpers import register_docstring


@register_docstring('rst')
def generate_rst_docstring(fn_types: FunctionTypes, indent='') -> str:

    docstring = [
        '', f"{indent}'''",
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

    docstring.append(f"{indent}'''\n")

    return '\n'.join(docstring)
