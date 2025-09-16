import json
from pathlib import Path

from dococtopy.core.engine import scan_paths
from dococtopy.reporters.json_reporter import to_dict, to_json


def test_json_reporter_structure(tmp_path: Path) -> None:
    p = tmp_path / "m.py"
    p.write_text("def a():\n\tpass\n")
    report, stats = scan_paths([p])
    data = to_dict(report)
    assert "version" in data
    assert "summary" in data and "files_total" in data["summary"]
    assert isinstance(data["files"], list)
    s = to_json(report)
    parsed = json.loads(s)
    assert parsed["files"][0]["path"].endswith("m.py")
