"""Python adapter: parse module and list symbols with docstrings.

MVP: expose functions and classes with names, kind, and docstring presence.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional


@dataclass
class PythonSymbol:
    name: str
    kind: str  # "module" | "function" | "class"
    lineno: int
    col: int
    docstring: Optional[str]
    ast_node: Optional[ast.AST] = None


def parse_module(text: str, path: Path) -> ast.Module:
    return ast.parse(text, filename=str(path))


def iter_symbols(mod: ast.Module) -> Iterator[PythonSymbol]:
    # Module as a symbol
    yield PythonSymbol(
        name="<module>",
        kind="module",
        lineno=1,
        col=0,
        docstring=ast.get_docstring(mod),
        ast_node=mod,
    )
    for node in mod.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            yield PythonSymbol(
                name=node.name,
                kind="function",
                lineno=getattr(node, "lineno", 1),
                col=getattr(node, "col_offset", 0),
                docstring=ast.get_docstring(node),
                ast_node=node,
            )
        elif isinstance(node, ast.ClassDef):
            yield PythonSymbol(
                name=node.name,
                kind="class",
                lineno=getattr(node, "lineno", 1),
                col=getattr(node, "col_offset", 0),
                docstring=ast.get_docstring(node),
                ast_node=node,
            )


def load_symbols_from_file(path: Path) -> list[PythonSymbol]:
    text = path.read_text(encoding="utf-8")
    mod = parse_module(text, path)
    return list(iter_symbols(mod))
