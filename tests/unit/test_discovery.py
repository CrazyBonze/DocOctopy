import importlib.util
import os
from pathlib import Path

import pytest  # type: ignore[import]

from dococtopy.core.discovery import discover_python_files


def write(p: Path, content: str = "") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def test_discovers_python_files_in_directory(tmp_path: Path) -> None:
    write(tmp_path / "a.py", "# a")
    write(tmp_path / "b/b.py", "# b")
    write(tmp_path / "c.txt", "not py")

    files = discover_python_files([tmp_path])
    rels = sorted(str(p.relative_to(tmp_path)) for p in files)
    assert rels == ["a.py", os.path.join("b", "b.py")]


def test_includes_direct_file_argument(tmp_path: Path) -> None:
    f = tmp_path / "only.py"
    write(f, "# only")
    files = discover_python_files([f])
    assert files == [f]


_HAS_PATHSPEC = importlib.util.find_spec("pathspec") is not None


@pytest.mark.skipif(not _HAS_PATHSPEC, reason="pathspec not installed")
def test_respects_gitignore_when_pathspec_available(tmp_path: Path) -> None:
    write(tmp_path / ".gitignore", "ignored_dir/\nignored.py\n")
    write(tmp_path / "kept.py", "# kept")
    write(tmp_path / "ignored.py", "# ignored")
    write(tmp_path / "ignored_dir" / "inside.py", "# ignored sub")

    files = discover_python_files([tmp_path])
    rels = {str(p.relative_to(tmp_path)) for p in files}
    assert "kept.py" in rels
    assert "ignored.py" not in rels
    assert os.path.join("ignored_dir", "inside.py") not in rels


def test_extra_excludes_patterns(tmp_path: Path) -> None:
    write(tmp_path / "keep.py", "# keep")
    write(tmp_path / "skip.py", "# skip")
    files = discover_python_files([tmp_path], extra_excludes=["skip.py"])
    rels = {str(p.relative_to(tmp_path)) for p in files}
    assert "keep.py" in rels
    assert "skip.py" not in rels
