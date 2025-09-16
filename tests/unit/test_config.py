from pathlib import Path

from dococtopy.core.config import load_config


def test_loads_exclude_and_rules(tmp_path: Path) -> None:
    py = tmp_path / "pyproject.toml"
    py.write_text(
        """
[tool.docguard]
exclude = ["**/build/**", "ignore.py"]
[tool.docguard.rules]
DG101 = "off"
"""
    )
    cfg = load_config(py)
    assert cfg is not None
    assert "ignore.py" in cfg.exclude
    assert cfg.is_rule_enabled("DG101") is False
