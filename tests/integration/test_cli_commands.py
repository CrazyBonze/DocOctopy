import subprocess
import sys
from pathlib import Path


def test_cli_help_commands() -> None:
    """Test that CLI help commands work."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy", "--help"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    assert result.returncode == 0
    assert "docstyle compliance" in result.stdout
    assert "scan" in result.stdout


def test_cli_scan_help() -> None:
    """Test that scan command help works."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy", "scan", "--help"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    assert result.returncode == 0
    assert "--format" in result.stdout
    assert "--no-cache" in result.stdout
    assert "--changed-only" in result.stdout
    assert "--stats" in result.stdout
    assert "--output-file" in result.stdout


def test_cli_config_init_help() -> None:
    """Test that config init command help works."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy", "config-init", "--help"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    assert result.returncode == 0
    assert "config" in result.stdout.lower()


def test_cli_version() -> None:
    """Test that version command works."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy", "--version"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
