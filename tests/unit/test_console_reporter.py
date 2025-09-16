from io import StringIO
from pathlib import Path

from dococtopy.core.engine import scan_paths
from dococtopy.reporters.console import print_report


def test_console_reporter_output(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    report, stats = scan_paths([p])
    buf = StringIO()
    print_report(report, buf, stats=stats)
    out = buf.getvalue()
    assert "Scan Results" in out
    assert "Files scanned" in out
    assert "NON_COMPLIANT" in out or "OK" in out
    assert "Cache:" in out
