from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # avoid typing cycles in static analyzers
    from dococtopy.core.findings import ScanReport


def to_dict(report) -> dict[str, Any]:
    # Pydantic-like models may not be real pydantic here; build manually
    files = []
    for fr in report.files:
        files.append(
            {
                "path": str(fr.path),
                "coverage": fr.coverage,
                "findings": [
                    {
                        "rule": f.rule_id,
                        "level": (
                            f.level.value if hasattr(f.level, "value") else str(f.level)
                        ),
                        "symbol": f.symbol,
                        "message": f.message,
                        "location": {"line": f.location.line, "col": f.location.column},
                        "suggestion": f.suggestion,
                    }
                    for f in fr.findings
                ],
            }
        )
    return {
        "version": report.version if hasattr(report, "version") else "1.0",
        "summary": {
            "files_total": report.summary.files_total,
            "files_compliant": report.summary.files_compliant,
            "coverage_overall": report.summary.coverage_overall,
        },
        "files": files,
    }


def to_json(report) -> str:
    # Single-line JSON for easier CLI parsing
    return json.dumps(to_dict(report), separators=(",", ":"), sort_keys=False)
