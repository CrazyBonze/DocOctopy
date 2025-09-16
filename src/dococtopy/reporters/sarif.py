from __future__ import annotations

from typing import Any, Dict


def to_sarif(report) -> Dict[str, Any]:
    """Convert ScanReport to SARIF format for GitHub Code Scanning.

    Returns a minimal SARIF 2.1.0 report structure.
    """
    runs = []
    results = []
    rules = []

    # Collect unique rules
    rule_ids = set()
    for fr in report.files:
        for f in fr.findings:
            rule_ids.add(f.rule_id)

    # Build rules array
    for rule_id in sorted(rule_ids):
        rules.append(
            {
                "id": rule_id,
                "name": rule_id,  # Could be enhanced with rule descriptions
                "shortDescription": {"text": f"Docstring compliance rule {rule_id}"},
                "defaultConfiguration": {"level": "error"},
            }
        )

    # Build results array
    for fr in report.files:
        for f in fr.findings:
            results.append(
                {
                    "ruleId": f.rule_id,
                    "level": "error" if f.level.value == "error" else "warning",
                    "message": {"text": f.message},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": str(fr.path)},
                                "region": {
                                    "startLine": f.location.line,
                                    "startColumn": f.location.column,
                                },
                            }
                        }
                    ],
                }
            )

    runs.append(
        {
            "tool": {
                "driver": {"name": "DocOctopy", "version": "0.1.0", "rules": rules}
            },
            "results": results,
        }
    )

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": runs,
    }
