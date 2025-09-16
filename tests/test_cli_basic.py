"""
Basic CLI tests to drive initial development.
"""

import subprocess
import sys
from pathlib import Path


def test_cli_exists_and_runs():
    """Test that the CLI exists and can be invoked."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy.cli.main", "--help"],
        capture_output=True,
        text=True,
    )

    # Should exit cleanly
    assert result.returncode == 0

    # Should have basic help content
    assert "dococtopy" in result.stdout.lower()
    assert "scan" in result.stdout.lower()


def test_cli_version():
    """Test that the CLI can report its version."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy.cli.main", "--version"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_scan_command_exists():
    """Test that the scan command exists and shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy.cli.main", "scan", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "scan" in result.stdout.lower()
    assert "path" in result.stdout.lower()  # Should accept paths


def test_scan_nonexistent_path():
    """Test that scanning a nonexistent path fails gracefully."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy.cli.main", "scan", "/nonexistent/path"],
        capture_output=True,
        text=True,
    )

    # Should exit with error code but not crash
    assert result.returncode != 0
    # Should have some error message
    assert len(result.stderr) > 0 or "error" in result.stdout.lower()


def test_scan_empty_directory(tmp_path):
    """Test scanning an empty directory."""
    result = subprocess.run(
        [sys.executable, "-m", "dococtopy.cli.main", "scan", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0
    # Should indicate no files found or similar
    assert "0" in result.stdout or "no files" in result.stdout.lower()
