from pathlib import Path

from dococtopy.core.cache import (
    CacheEntry,
    compute_fingerprint,
    deserialize_file_result,
    load_cache,
    save_cache,
    serialize_file_result,
)
from dococtopy.core.engine import scan_paths


def test_compute_fingerprint_changes_with_content(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("def a():\n\tpass\n")
    fp1 = compute_fingerprint(f, {}, ["DG101"])  # rules map empty/off
    f.write_text('def a():\n\t"""doc"""\n\tpass\n')
    fp2 = compute_fingerprint(f, {}, ["DG101"])
    assert fp1 != fp2


def test_cache_roundtrip_file_result(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("def a():\n\tpass\n")
    report, stats = scan_paths([f], config=None, use_cache=False)
    fr = report.files[0]
    store = load_cache(tmp_path)
    entry = CacheEntry(fingerprint="x", file_result=serialize_file_result(fr))
    store.set(f, entry)
    save_cache(store)
    store2 = load_cache(tmp_path)
    ce2 = store2.get(f)
    assert ce2 is not None
    fr2 = deserialize_file_result(ce2.file_result)
    assert fr2.path == fr.path and len(fr2.findings) == len(fr.findings)
