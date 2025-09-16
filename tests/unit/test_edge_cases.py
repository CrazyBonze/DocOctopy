import json
import tempfile
from pathlib import Path

from dococtopy.core.cache import CacheEntry, CacheStore, load_cache, save_cache
from dococtopy.core.config import Config, load_config
from dococtopy.core.discovery import discover_python_files
from dococtopy.core.engine import _compute_coverage, _overall_coverage, scan_paths
from dococtopy.core.findings import (
    FileScanResult,
    Finding,
    FindingLevel,
    Location,
    ScanReport,
    ScanSummary,
)


def test_cache_error_handling(tmp_path: Path) -> None:
    """Test cache handles errors gracefully."""
    # Test loading from non-existent file
    cache = load_cache(tmp_path / "nonexistent")
    assert len(cache.entries) == 0

    # Test saving to invalid path (should not crash)
    invalid_cache = CacheStore(path=Path("/invalid/path/cache.json"))
    invalid_cache.set(Path("test.py"), CacheEntry(fingerprint="x", file_result={}))
    save_cache(invalid_cache)  # Should not raise


def test_config_error_handling(tmp_path: Path) -> None:
    """Test config handles malformed files gracefully."""
    # Test loading non-existent config - should return None
    config = load_config(tmp_path / "nonexistent.toml")
    assert config is None

    # Test malformed TOML - should return None due to parsing error
    bad_config = tmp_path / "bad.toml"
    bad_config.write_text("[invalid toml content")
    config = load_config(bad_config)
    assert config is None  # Should return None due to parsing error


def test_discovery_edge_cases(tmp_path: Path) -> None:
    """Test file discovery edge cases."""
    # Test empty directory
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    files = discover_python_files([empty_dir])
    assert len(files) == 0

    # Test non-existent path
    files = discover_python_files([tmp_path / "nonexistent"])
    assert len(files) == 0

    # Test mixed paths (some exist, some don't)
    existing_file = tmp_path / "test.py"
    existing_file.write_text("def test(): pass")
    files = discover_python_files([existing_file, tmp_path / "nonexistent"])
    assert len(files) == 1
    assert files[0] == existing_file


def test_engine_coverage_functions() -> None:
    """Test coverage calculation functions."""
    # Test _compute_coverage with empty symbols
    coverage = _compute_coverage([])
    assert coverage == 1.0

    # Test _overall_coverage with empty files
    coverage = _overall_coverage([])
    assert coverage == 1.0


def test_findings_edge_cases() -> None:
    """Test findings model edge cases."""
    # Test Finding with minimal data
    finding = Finding(
        rule_id="TEST",
        level=FindingLevel.ERROR,
        message="Test message",
        symbol=None,
        location=Location(line=1, column=0),
        suggestion=None,
    )
    assert finding.rule_id == "TEST"
    assert finding.level == FindingLevel.ERROR

    # Test FileScanResult with empty findings
    result = FileScanResult(path=Path("test.py"), findings=[], coverage=0.5)
    assert result.coverage == 0.5
    assert len(result.findings) == 0


def test_scan_paths_edge_cases(tmp_path: Path) -> None:
    """Test scan_paths with edge cases."""
    # Test with empty paths
    report, stats = scan_paths([])
    assert report.summary.files_total == 0
    assert stats["files_processed"] == 0

    # Test with non-existent paths
    report, stats = scan_paths([tmp_path / "nonexistent"])
    assert report.summary.files_total == 0

    # Test with no-cache mode
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    report, stats = scan_paths([test_file], use_cache=False)
    assert report.summary.files_total == 1
    assert stats["cache_misses"] == 1
