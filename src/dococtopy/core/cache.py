from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:  # avoid circular typing issues
    from dococtopy.core.findings import FileScanResult, Finding, FindingLevel, Location

from dococtopy.core.findings import Finding, FindingLevel, Location  # runtime imports

CACHE_DIRNAME = ".dococtopy"
CACHE_FILENAME = "cache_v1.json"
RULESET_VERSION = "ruleset-1"  # bump if rule semantics change broadly


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_fingerprint(
    file_path: Path, config_rules: Dict[str, str] | None, rule_ids: list[str]
) -> str:
    content = file_path.read_bytes()
    base = _sha256_bytes(content)
    rules_json = json.dumps(config_rules or {}, sort_keys=True)
    rules_part = _sha256_bytes(rules_json.encode("utf-8"))
    rule_ids_part = _sha256_bytes("|".join(sorted(rule_ids)).encode("utf-8"))
    version_part = RULESET_VERSION
    return ":".join([base, rules_part, rule_ids_part, version_part])


@dataclass
class CacheEntry:
    fingerprint: str
    file_result: Dict[str, Any]  # serialized FileScanResult


@dataclass
class CacheStore:
    path: Path
    entries: Dict[str, CacheEntry] = field(default_factory=dict)

    def get(self, file_path: Path) -> Optional[CacheEntry]:
        return self.entries.get(str(file_path))

    def set(self, file_path: Path, entry: CacheEntry) -> None:
        self.entries[str(file_path)] = entry


def _cache_file(root: Path) -> Path:
    return root / CACHE_DIRNAME / CACHE_FILENAME


def load_cache(root: Path) -> CacheStore:
    cf = _cache_file(root)
    if not cf.exists():
        return CacheStore(path=cf)
    try:
        data = json.loads(cf.read_text(encoding="utf-8"))
        entries: Dict[str, CacheEntry] = {}
        for k, v in data.get("entries", {}).items():
            entries[k] = CacheEntry(
                fingerprint=v["fingerprint"], file_result=v["file_result"]
            )
        return CacheStore(path=cf, entries=entries)
    except Exception:
        return CacheStore(path=cf)


def save_cache(store: CacheStore) -> None:
    try:
        store.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "entries": {
                k: {"fingerprint": e.fingerprint, "file_result": e.file_result}
                for k, e in store.entries.items()
            }
        }
        store.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        # Best-effort cache; ignore failures
        pass


def serialize_file_result(res) -> Dict[str, Any]:
    return {
        "path": str(res.path),
        "coverage": res.coverage,
        "findings": [
            {
                "rule_id": f.rule_id,
                "level": f.level.value if hasattr(f.level, "value") else str(f.level),
                "message": f.message,
                "symbol": f.symbol,
                "location": {"line": f.location.line, "column": f.location.column},
                "suggestion": f.suggestion,
            }
            for f in res.findings
        ],
    }


def deserialize_file_result(data: Dict[str, Any]):
    findings: list[Finding] = []
    for fd in data.get("findings", []):
        findings.append(
            Finding(  # type: ignore[call-arg]
                rule_id=fd["rule_id"],
                level=FindingLevel(fd["level"]),
                message=fd["message"],
                symbol=fd.get("symbol"),
                location=Location(
                    line=fd["location"]["line"], column=fd["location"]["column"]
                ),
                suggestion=fd.get("suggestion"),
            )
        )
    from dococtopy.core.findings import FileScanResult  # local import to avoid cycles

    return FileScanResult(  # type: ignore[call-arg]
        path=Path(data["path"]),
        findings=findings,
        coverage=float(data.get("coverage", 1.0)),
    )
