"""
File discovery utilities.

MVP: enumerate Python source files under provided paths while respecting
basic ignore patterns. If a ``.gitignore`` is present at or above the
provided root, we use ``pathspec`` to filter ignored paths. Callers can
add extra glob patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

try:
    from pathspec import PathSpec  # type: ignore
    from pathspec.patterns.gitwildmatch import GitWildMatchPattern  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    PathSpec = None  # type: ignore
    GitWildMatchPattern = None  # type: ignore


def _load_gitignore(root: Path) -> list[str]:
    """Load .gitignore patterns from root upwards until filesystem root.

    Returns an empty list if no .gitignore files found or pathspec is missing.
    """
    patterns: list[str] = []
    if PathSpec is None:
        return patterns

    current = root.resolve()
    visited: set[Path] = set()
    while True:
        if current in visited:
            break
        visited.add(current)
        gi = current / ".gitignore"
        if gi.is_file():
            try:
                patterns.extend(gi.read_text().splitlines())
            except Exception:
                pass
        if current.parent == current:
            break
        current = current.parent
    return patterns


def _build_spec(patterns: Sequence[str] | None):
    if PathSpec is None or GitWildMatchPattern is None:
        return None
    merged = [p for p in (patterns or []) if p and not p.strip().startswith("#")]
    return PathSpec.from_lines(GitWildMatchPattern, merged)


def discover_python_files(
    paths: Iterable[Path], extra_excludes: Sequence[str] | None = None
) -> List[Path]:
    """Discover ``.py`` files under given paths honoring ignore patterns.

    - Direct file arguments ending with ``.py`` are included unless ignored
    - Directories are recursively searched for ``*.py`` files
    - ``.gitignore`` patterns from path roots are respected when pathspec is available
    - ``extra_excludes`` can provide additional gitwildmatch-style patterns
    """
    collected: list[Path] = []
    path_list = [Path(p) for p in paths]
    # Build a union pathspec from all roots
    all_patterns: list[str] = []
    roots: set[Path] = set()
    for p in path_list:
        root = p if p.is_dir() else p.parent
        roots.add(root)
    for r in roots:
        all_patterns.extend(_load_gitignore(r))
    if extra_excludes:
        all_patterns.extend(list(extra_excludes))
    spec = _build_spec(all_patterns)

    def is_ignored(path: Path) -> bool:
        if spec is None:
            return False
        try:
            # Evaluate relative to the nearest root provided
            for root in roots:
                try:
                    rel = path.resolve().relative_to(root.resolve())
                    if spec.match_file(str(rel)):
                        return True
                except Exception:
                    continue
        except Exception:
            return False
        return False

    for path in path_list:
        if path.is_file() and path.suffix == ".py":
            if not is_ignored(path):
                collected.append(path)
            continue
        if path.is_dir():
            for file_path in path.rglob("*.py"):
                if not is_ignored(file_path):
                    collected.append(file_path)
    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in collected:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique
