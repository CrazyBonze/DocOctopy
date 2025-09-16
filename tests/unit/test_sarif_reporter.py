from pathlib import Path

from dococtopy.core.engine import scan_paths
from dococtopy.reporters.sarif import to_sarif


def test_sarif_reporter_structure(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    report, stats = scan_paths([p])
    sarif = to_sarif(report)
    assert sarif["version"] == "2.1.0"
    assert "$schema" in sarif
    assert "runs" in sarif
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert "tool" in run
    assert "results" in run
    assert run["tool"]["driver"]["name"] == "DocOctopy"
