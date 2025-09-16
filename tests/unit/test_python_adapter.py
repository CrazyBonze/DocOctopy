from pathlib import Path

from dococtopy.adapters.python.adapter import load_symbols_from_file


def test_load_symbols_module_func_class(tmp_path: Path) -> None:
    code = '"""Module doc."""\n\nclass C:\n\t"""C doc"""\n\tdef m(self):\n\t\tpass\n\n\ndef f():\n\t"""f doc"""\n\treturn 1\n'
    p = tmp_path / "m.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    names = [s.name for s in syms]
    assert names[0] == "<module>"
    assert "C" in names
    assert "f" in names
    kinds = {s.name: s.kind for s in syms}
    assert kinds["C"] == "class"
    assert kinds["f"] == "function"
