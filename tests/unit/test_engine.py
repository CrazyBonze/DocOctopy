from pathlib import Path

from dococtopy.core.engine import scan_paths


def test_engine_reports_findings_and_coverage(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    report, stats = scan_paths([p])
    assert report.summary.files_total == 1
    assert report.summary.files_compliant == 0
    assert report.files[0].path == p
    assert any(f.rule_id == "DG101" for f in report.files[0].findings)
    assert 0.0 <= report.summary.coverage_overall <= 1.0
    assert "cache_hits" in stats and "cache_misses" in stats
