"""Docstring validation and trivial fix detection.

This module provides validation of generated docstrings and detection
of trivial fixes that can be handled without LLM calls.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.core.findings import Finding
from dococtopy.rules.registry import all_rules


@dataclass
class ValidationResult:
    """Result of docstring validation."""

    is_valid: bool
    findings: List[Finding]
    trivial_fixes_applied: List[str]


class DocstringValidator:
    """Validates generated docstrings against compliance rules."""

    def __init__(self, config=None):
        """Initialize validator with optional config."""
        self.config = config
        self.rules = {rule.id: rule for rule in all_rules()}

    def validate_docstring(
        self, symbol: PythonSymbol, docstring: str, file_path: Optional[Path] = None
    ) -> ValidationResult:
        """
        Validate a docstring against all enabled rules.

        Args:
            symbol: The Python symbol the docstring belongs to
            docstring: The docstring content to validate
            file_path: Optional file path for context

        Returns:
            ValidationResult with validation status and findings
        """
        # Create a temporary symbol with the new docstring for validation
        temp_symbol = PythonSymbol(
            name=symbol.name,
            kind=symbol.kind,
            lineno=symbol.lineno,
            col=symbol.col,
            docstring=docstring,
            ast_node=symbol.ast_node,
        )

        # Run all rules on the temporary symbol
        all_findings = []
        for rule in self.rules.values():
            try:
                findings = rule.check(symbols=[temp_symbol])
                all_findings.extend(findings)
            except Exception as e:
                # Log error but continue with other rules
                print(f"Warning: Rule {rule.id} failed during validation: {e}")

        # Filter findings based on config if available
        if self.config and hasattr(self.config, "rules"):
            enabled_rules = self.config.rules or {}
            filtered_findings = []
            for finding in all_findings:
                rule_config = enabled_rules.get(finding.rule_id, {})
                if rule_config.get("enabled", True):
                    filtered_findings.append(finding)
            all_findings = filtered_findings

        return ValidationResult(
            is_valid=len(all_findings) == 0,
            findings=all_findings,
            trivial_fixes_applied=[],
        )


class TrivialFixDetector:
    """Detects and applies trivial docstring fixes without LLM calls."""

    def __init__(self):
        """Initialize trivial fix detector."""
        self.fixers = {
            "DG301": self._fix_summary_period,
            "DG302": self._fix_blank_line_after_summary,
            "DG209": self._fix_summary_length,
        }

    def detect_and_fix(
        self, symbol: PythonSymbol, findings: List[Finding]
    ) -> Tuple[Optional[str], List[str]]:
        """
        Detect and apply trivial fixes for a symbol.

        Args:
            symbol: The Python symbol to fix
            findings: List of findings for this symbol

        Returns:
            Tuple of (fixed_docstring, list_of_applied_fixes)
            Returns (None, []) if no trivial fixes can be applied
        """
        if not symbol.docstring:
            return None, []

        docstring = symbol.docstring
        applied_fixes = []

        # Apply trivial fixes in order
        for finding in findings:
            rule_id = finding.rule_id
            if rule_id in self.fixers:
                try:
                    fixed_docstring = self.fixers[rule_id](docstring, finding)
                    if fixed_docstring != docstring:
                        docstring = fixed_docstring
                        applied_fixes.append(f"Fixed {rule_id}: {finding.message}")
                except Exception as e:
                    print(f"Warning: Failed to apply trivial fix for {rule_id}: {e}")

        if applied_fixes:
            return docstring, applied_fixes

        return None, []

    def _fix_summary_period(self, docstring: str, finding: Finding) -> str:
        """Fix missing period at end of summary line."""
        lines = docstring.split("\n")
        if not lines:
            return docstring

        first_line = lines[0].strip()
        if first_line and not first_line.endswith("."):
            lines[0] = first_line + "."
            return "\n".join(lines)

        return docstring

    def _fix_blank_line_after_summary(self, docstring: str, finding: Finding) -> str:
        """Fix missing blank line after summary."""
        lines = docstring.split("\n")
        if len(lines) < 2:
            return docstring

        # Check if first line is summary and second line is not blank
        first_line = lines[0].strip()
        second_line = lines[1].strip()

        if first_line and second_line and not second_line.startswith(" "):
            # Insert blank line after summary
            lines.insert(1, "")
            return "\n".join(lines)

        return docstring

    def _fix_summary_length(self, docstring: str, finding: Finding) -> str:
        """Fix summary length issues."""
        lines = docstring.split("\n")
        if not lines:
            return docstring

        first_line = lines[0].strip()
        if not first_line:
            return docstring

        # If summary is too short, try to make it more descriptive
        if len(first_line) < 10:
            # This is complex, so we'll skip it for now
            # Could be enhanced with heuristics based on function name/parameters
            return docstring

        # If summary is too long, truncate it
        if len(first_line) > 80:
            truncated = first_line[:77] + "..."
            lines[0] = truncated
            return "\n".join(lines)

        return docstring


class DocstringFixer:
    """Combines validation, trivial fixes, and LLM-based fixes."""

    def __init__(
        self, validator: DocstringValidator, trivial_detector: TrivialFixDetector
    ):
        """Initialize fixer with validator and trivial detector."""
        self.validator = validator
        self.trivial_detector = trivial_detector
        self.max_retries = 3

    def fix_docstring(
        self,
        symbol: PythonSymbol,
        original_findings: List[Finding],
        llm_client,
        file_path: Optional[Path] = None,
    ) -> Tuple[str, List[str], bool]:
        """
        Fix a docstring using trivial fixes and LLM as needed.

        Args:
            symbol: The Python symbol to fix
            original_findings: Original findings for this symbol
            llm_client: LLM client for complex fixes
            file_path: Optional file path for context

        Returns:
            Tuple of (fixed_docstring, applied_fixes, used_llm)
        """
        applied_fixes = []
        used_llm = False

        # First, try trivial fixes
        if symbol.docstring:
            trivial_fixed, trivial_fixes = self.trivial_detector.detect_and_fix(
                symbol, original_findings
            )
            if trivial_fixed:
                applied_fixes.extend(trivial_fixes)
                # Update symbol with trivial fixes
                symbol = PythonSymbol(
                    name=symbol.name,
                    kind=symbol.kind,
                    lineno=symbol.lineno,
                    col=symbol.col,
                    docstring=trivial_fixed,
                    ast_node=symbol.ast_node,
                )

        # Validate current state
        validation_result = self.validator.validate_docstring(
            symbol, symbol.docstring or "", file_path
        )

        if validation_result.is_valid:
            return symbol.docstring or "", applied_fixes, used_llm

        # If still not valid, use LLM with retry logic
        current_docstring = symbol.docstring or ""
        remaining_findings = validation_result.findings

        for attempt in range(self.max_retries):
            try:
                # Use LLM to fix remaining issues
                if not current_docstring:
                    # Generate new docstring
                    from dococtopy.remediation.prompts import PromptBuilder

                    context = PromptBuilder.build_function_context(symbol)
                    current_docstring = llm_client.generate_docstring(
                        function_signature=context.signature,
                        function_purpose="Function implementation",
                        existing_docstring="",
                        context="; ".join([f.message for f in remaining_findings]),
                    )
                else:
                    # Fix existing docstring
                    issues = "; ".join([f.message for f in remaining_findings])
                    current_docstring = llm_client.fix_docstring(
                        function_signature=symbol.signature,
                        current_docstring=current_docstring,
                        issues=issues,
                    )

                used_llm = True
                applied_fixes.append(f"LLM fix attempt {attempt + 1}")

                # Validate the LLM result
                validation_result = self.validator.validate_docstring(
                    symbol, current_docstring, file_path
                )

                if validation_result.is_valid:
                    return current_docstring, applied_fixes, used_llm

                remaining_findings = validation_result.findings

            except Exception as e:
                print(f"Warning: LLM fix attempt {attempt + 1} failed: {e}")
                continue

        # If all retries failed, return the best attempt
        print(
            f"Warning: Could not fully fix docstring for {symbol.name} after {self.max_retries} attempts"
        )
        return current_docstring, applied_fixes, used_llm
