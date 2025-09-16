from __future__ import annotations

from typing import TextIO

from dococtopy.core.findings import FindingLevel


def print_report(report, stream: TextIO, stats: dict[str, int] | None = None) -> None:
    stream.write("Scan Results\n")
    stream.write(f"Files scanned: {report.summary.files_total}\n")
    stream.write(f"Files compliant: {report.summary.files_compliant}\n")
    stream.write(f"Overall coverage: {report.summary.coverage_overall:.2%}\n")
    if stats:
        hit_rate = stats["cache_hits"] / max(stats["files_processed"], 1) * 100
        stream.write(
            f"Cache: {stats['cache_hits']} hits, {stats['cache_misses']} misses ({hit_rate:.1f}% hit rate)\n"
        )
    stream.write("\n")
    for fr in report.files:
        status = (
            "OK"
            if all(f.level != FindingLevel.ERROR for f in fr.findings)
            else "NON_COMPLIANT"
        )
        stream.write(f"- {fr.path} [{status}] (coverage {fr.coverage:.0%})\n")
        for f in fr.findings:
            stream.write(
                f"  {f.rule_id} [{f.level}]: {f.message}"
                f" at {f.location.line}:{f.location.column}\n"
            )
