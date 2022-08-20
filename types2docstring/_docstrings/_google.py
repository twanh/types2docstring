from types2docstring._helpers import FunctionTypes
from types2docstring._helpers import register_docstring


@register_docstring('google')
def google_docstrings(fn_types: FunctionTypes, indent='') -> str:
    return 'HI this is google'
