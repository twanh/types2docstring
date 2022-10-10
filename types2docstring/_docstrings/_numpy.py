from string import Template

from types2docstring._helpers import FunctionTypes
from types2docstring._helpers import register_docstring

NUMPY_TEMPLATE = """
${indent}\"\"\"[function description]

${indent}Parameters
${indent}----------
${indent}$args

${indent}Returns
${indent}-------
${indent}$returns

${indent}\"\"\"
"""

NUMPY_ARGS_TEMPLATE = """
${indent}$arg_name : $arg_type
${indent}\t[argument description]
"""

NUMPY_RETURNS_TEMPLATE = """
${indent}$type
${indent}\t[return description]
"""


@register_docstring('numpy')
def generate_numpy_docstring(fn_types: FunctionTypes, indent='') -> str:

    args = []
    args_str = 'No arguments'

    for arg in fn_types.args:
        if all(arg):
            arg_template = Template(NUMPY_ARGS_TEMPLATE)
            args.append(
                arg_template.substitute(
                    {'arg_name': arg[0], 'arg_type': arg[1], 'indent': indent},
                ),
            )
    if len(args) > 0:
        args_str = f'\n{indent}\t'.join(args)

    ret_str = Template(NUMPY_RETURNS_TEMPLATE).substitute(
        {'type': fn_types.returns, 'indent': indent},
    )

    gt = Template(NUMPY_TEMPLATE)
    fin = gt.substitute(
        {'args': args_str, 'returns': ret_str, 'indent': indent},
    )
    return fin
