import pkgutil
from typing import Callable
from typing import NamedTuple

from types2docstring import _docstrings


class FunctionTypes(NamedTuple):
    args: list[tuple[str, str | None]]
    returns: str


DOCSTRING_FUNC = Callable[[FunctionTypes, str], str]

DOCSTRING_TYPES: list[tuple[str, DOCSTRING_FUNC]] = []


def register_docstring(
    name: str,
) -> Callable[[DOCSTRING_FUNC], DOCSTRING_FUNC]:
    def register_docstring_decorator(func: DOCSTRING_FUNC) -> DOCSTRING_FUNC:
        DOCSTRING_TYPES.append((name, func))
        return func
    return register_docstring_decorator


def _import_docstrings() -> None:
    """
    Imports all docstring (types) in _docstrings directory.

    All the type of docstrings still have to be registered
    with their correct decorator.
    """

    docstring_path = _docstrings.__path__
    mod_infos = pkgutil.walk_packages(
        docstring_path, f'{_docstrings.__name__}.',
    )
    for _, name, _ in mod_infos:
        __import__(name, fromlist=['_trash'])


_import_docstrings()
