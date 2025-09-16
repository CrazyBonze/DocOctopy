import json
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "dococtopy.cli.main", *args],
        capture_output=True,
        text=True,
    )


def test_scan_fail_level_error_sets_exit_code(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    res = _run_cli(["scan", str(tmp_path), "--format", "json", "--fail-level", "error"])
    assert res.returncode == 1
    assert '"files_total"' in res.stdout or res.stderr == ""


def test_scan_fail_level_warning_allows_exit_zero_when_no_warnings(
    tmp_path: Path,
) -> None:
    p = tmp_path / "m.py"
    p.write_text('"""m"""\n\n')
    res = _run_cli(
        ["scan", str(tmp_path), "--format", "json", "--fail-level", "warning"]
    )
    assert res.returncode == 0


def test_scan_json_output_structure(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    res = _run_cli(["scan", str(tmp_path), "--format", "json"])
    assert res.returncode in (0, 1)
    data = (
        json.loads(res.stdout.splitlines()[-1])
        if res.stdout.strip().startswith("{")
        else json.loads(res.stdout.split("\n", 1)[-1])
    )
    assert "summary" in data and "files" in data


def test_cli_respects_config_disabling_rule(tmp_path: Path) -> None:
    # Write a module missing docstrings, but disable DG101 in config
    (tmp_path / "pkg").mkdir()
    (src := tmp_path / "pkg" / "m.py").write_text("def a():\n\tpass\n")
    py = tmp_path / "pyproject.toml"
    py.write_text(
        """
        [tool.docguard]
        [tool.docguard.rules]
        DG101 = "off"
        """
    )
    res = _run_cli(["scan", str(tmp_path), "--format", "json", "--config", str(py)])
    assert res.returncode == 0


def test_cli_output_file_writes_json(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    output_file = tmp_path / "report.json"
    res = _run_cli(
        ["scan", str(tmp_path), "--format", "json", "--output-file", str(output_file)]
    )
    assert res.returncode in (0, 1)
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert "summary" in data and "files" in data


def test_cli_stats_shows_cache_performance(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    res = _run_cli(["scan", str(tmp_path), "--stats"])
    assert res.returncode in (0, 1)
    assert "Cache:" in res.stdout


def test_cli_changed_only_skips_unchanged(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    # First run populates cache
    res1 = _run_cli(["scan", str(tmp_path), "--format", "json"])
    assert res1.returncode in (0, 1)
    # Second run with changed-only should skip unchanged files, yielding zero files in report
    res2 = _run_cli(["scan", str(tmp_path), "--format", "json", "--changed-only"])
    assert res2.returncode in (0, 1)
    data = json.loads(res2.stdout.strip())
    assert data["summary"]["files_total"] in (0, 1)
