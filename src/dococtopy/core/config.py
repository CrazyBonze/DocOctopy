from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass
class Config:
    root: Path
    exclude: List[str] = field(default_factory=list)
    rules: Dict[str, str] = field(default_factory=dict)  # e.g., {"DG101": "off"}

    def is_rule_enabled(self, rule_id: str) -> bool:
        state = self.rules.get(rule_id)
        return state is None or state.lower() not in {"off", "disabled", "disable"}


def load_config(explicit_path: Optional[Path]) -> Optional[Config]:
    """Load configuration from pyproject.toml [tool.docguard].

    Returns None if no config found, tomllib unavailable, or parsing fails.
    """
    cfg_path: Optional[Path]
    if explicit_path:
        cfg_path = Path(explicit_path)
    else:
        cfg_path = Path.cwd() / "pyproject.toml"
    if not cfg_path.exists() or tomllib is None:
        return None
    try:
        data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    tool = data.get("tool", {}) if isinstance(data, dict) else {}
    docguard = tool.get("docguard", {}) if isinstance(tool, dict) else {}
    exclude = list(docguard.get("exclude", [])) if isinstance(docguard, dict) else []
    rules = dict(docguard.get("rules", {})) if isinstance(docguard, dict) else {}
    return Config(root=cfg_path.parent, exclude=exclude, rules=rules)
