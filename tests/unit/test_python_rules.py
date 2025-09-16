from pathlib import Path

from dococtopy.adapters.python.adapter import load_symbols_from_file
from dococtopy.rules.python_rules import (
    DG101MissingDocstring,
    DG301SummaryStyle,
    DG302BlankLineAfterSummary,
)


def test_dg101_reports_missing_docstrings(tmp_path: Path) -> None:
    code = "def a():\n\tpass\n\nclass B:\n\tpass\n"
    p = tmp_path / "x.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    rule = DG101MissingDocstring()
    findings = rule.check(symbols=syms)
    ids = {getattr(f, "rule_id", None) for f in findings}
    assert "DG101" in ids
    messages = "\n".join(getattr(f, "message", "") for f in findings)
    assert "Function 'a' is missing a docstring" in messages
    assert "Class 'B' is missing a docstring" in messages


def test_dg301_summary_requires_period(tmp_path: Path) -> None:
    code = 'def f():\n\t"""Do thing\n\nReturns:\n\tNone\n"""\n\treturn 1\n'
    p = tmp_path / "m.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    findings = DG301SummaryStyle().check(symbols=syms)
    assert any(getattr(f, "rule_id", None) == "DG301" for f in findings)


def test_dg302_blank_line_after_summary(tmp_path: Path) -> None:
    code = 'def f():\n\t"""Summary without blank line\nDetails start immediately\n"""\n\treturn 1\n'
    p = tmp_path / "m.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    findings = DG302BlankLineAfterSummary().check(symbols=syms)
    assert any(getattr(f, "rule_id", None) == "DG302" for f in findings)
