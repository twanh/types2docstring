from string import Template

from types2docstring._helpers import FunctionTypes
from types2docstring._helpers import register_docstring

GOOGLE_TEMPLATE = """
${indent}\"\"\"[function description]

${indent}Args:
${indent}\t$args

${indent}Returns:
${indent}\t$returns
${indent}\"\"\"
"""
GOOGLE_ARG_TYPE_TEMPALTE = '$arg_name ($arg_type): [argument description]'
GOOGLE_RETURN_TEMPLATE = '$type: [return description]'


@register_docstring('google')
def google_docstrings(fn_types: FunctionTypes, indent='') -> str:

    args = []
    args_str = 'No arguments'
    # Generate arguments text
    for arg in fn_types.args:
        if all(arg):
            arg_template = Template(GOOGLE_ARG_TYPE_TEMPALTE)
            args.append(
                arg_template.substitute(
                    {'arg_name': arg[0], 'arg_type': arg[1]},
                ),
            )
    if len(args) > 0:
        args_str = f'\n{indent}\t'.join(args)
    # Generate return text
    ret_str = Template(GOOGLE_RETURN_TEMPLATE).substitute(
        {'type': fn_types.returns},
    )
    # Generate full docstring

    gt = Template(GOOGLE_TEMPLATE)
    fin = gt.substitute(
        {'args': args_str, 'returns': ret_str, 'indent': indent},
    )
    return fin
