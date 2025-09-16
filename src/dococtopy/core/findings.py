"""
Core data models for findings and results.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class FindingLevel(str, Enum):
    """Severity levels for findings."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Location(BaseModel):
    """Location of a finding in source code."""

    line: int = Field(description="Line number (1-based)")
    column: int = Field(default=0, description="Column number (0-based)")

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"


class Finding(BaseModel):
    """A single documentation compliance finding."""

    rule_id: str = Field(description="Rule identifier (e.g., 'DG101')")
    level: FindingLevel = Field(description="Severity level")
    message: str = Field(description="Human-readable description")
    symbol: Optional[str] = Field(
        default=None, description="Symbol name (function, class, etc.)"
    )
    location: Location = Field(description="Source location")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")

    def __str__(self) -> str:
        symbol_part = f" in '{self.symbol}'" if self.symbol else ""
        return f"{self.rule_id}: {self.message}{symbol_part} at {self.location}"


class FileScanResult(BaseModel):
    """Results for scanning a single file."""

    path: Path = Field(description="File path that was scanned")
    findings: list[Finding] = Field(default_factory=list, description="Issues found")
    coverage: float = Field(default=1.0, description="Documentation coverage (0.0-1.0)")

    @property
    def is_compliant(self) -> bool:
        """True if no error-level findings."""
        return not any(f.level == FindingLevel.ERROR for f in self.findings)

    @property
    def error_count(self) -> int:
        """Number of error-level findings."""
        return sum(1 for f in self.findings if f.level == FindingLevel.ERROR)

    @property
    def warning_count(self) -> int:
        """Number of warning-level findings."""
        return sum(1 for f in self.findings if f.level == FindingLevel.WARNING)


class ScanSummary(BaseModel):
    """Overall summary of scan results."""

    files_total: int = Field(description="Total files scanned")
    files_compliant: int = Field(description="Files with no error-level findings")
    coverage_overall: float = Field(description="Overall documentation coverage")

    @property
    def files_noncompliant(self) -> int:
        """Number of non-compliant files."""
        return self.files_total - self.files_compliant


class ScanReport(BaseModel):
    """Complete scan report."""

    version: str = Field(default="1.0", description="Report format version")
    summary: ScanSummary = Field(description="Overall summary")
    files: list[FileScanResult] = Field(
        default_factory=list, description="Per-file results"
    )

    def get_all_findings(self) -> list[Finding]:
        """Get all findings across all files."""
        findings = []
        for file_result in self.files:
            findings.extend(file_result.findings)
        return findings

    def has_errors(self) -> bool:
        """True if any error-level findings exist."""
        return any(f.level == FindingLevel.ERROR for f in self.get_all_findings())
