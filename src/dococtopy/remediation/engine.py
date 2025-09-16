"""Main remediation engine for docstring fixes.

This module orchestrates the LLM-based remediation process,
coordinating between the LLM client, prompt builder, and diff generator.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.core.findings import Finding, FindingLevel
from dococtopy.remediation.diff import ChangeTracker, DiffGenerator, DocstringChange
from dococtopy.remediation.llm import LLMClient, LLMConfig, create_llm_client
from dococtopy.remediation.prompts import FunctionContext, PromptBuilder


@dataclass
class RemediationOptions:
    """Options for docstring remediation."""

    dry_run: bool = True
    interactive: bool = False
    rule_ids: Optional[Set[str]] = None
    max_changes: Optional[int] = None
    llm_config: Optional[LLMConfig] = None


class RemediationEngine:
    """Main engine for docstring remediation."""

    def __init__(self, options: RemediationOptions):
        self.options = options
        self.llm_client = create_llm_client(
            options.llm_config
            or LLMConfig(
                provider="openai",
                model="gpt-4o-mini",
            )
        )
        self.change_tracker = ChangeTracker()

    def remediate_symbol(
        self,
        symbol: PythonSymbol,
        findings: List[Finding],
        file_path: Path,
    ) -> Optional[DocstringChange]:
        """Remediate a single symbol's docstring."""
        # Filter findings for this symbol
        symbol_findings = [f for f in findings if f.symbol == symbol.name]
        if not symbol_findings:
            return None

        # Filter by rule IDs if specified
        if self.options.rule_ids:
            symbol_findings = [
                f for f in symbol_findings if f.rule_id in self.options.rule_ids
            ]
            if not symbol_findings:
                return None

        # Build function context
        context = PromptBuilder.build_function_context(symbol)

        # Determine remediation strategy
        if not symbol.docstring:
            # Generate new docstring
            new_docstring = self._generate_new_docstring(context, symbol_findings)
            change_type = "added"
        else:
            # Fix existing docstring
            new_docstring = self._fix_existing_docstring(
                context, symbol.docstring, symbol_findings
            )
            change_type = "modified"

        if new_docstring == symbol.docstring:
            return None  # No change needed

        # Create change record
        change = DocstringChange(
            symbol_name=symbol.name,
            symbol_kind=symbol.kind,
            file_path=str(file_path),
            line_number=symbol.lineno,
            original_docstring=symbol.docstring or "",
            new_docstring=new_docstring,
            change_type=change_type,
            issues_addressed=[f.rule_id for f in symbol_findings],
        )

        return change

    def _generate_new_docstring(
        self,
        context: FunctionContext,
        findings: List[Finding],
    ) -> str:
        """Generate a new docstring for a symbol without one."""
        # Extract purpose from findings or use default
        purpose = self._extract_purpose_from_findings(findings)

        # Generate docstring using LLM
        return self.llm_client.generate_docstring(
            function_signature=context.signature,
            function_purpose=purpose,
            existing_docstring="",
            context=self._build_context_from_findings(findings),
        )

    def _fix_existing_docstring(
        self,
        context: FunctionContext,
        current_docstring: str,
        findings: List[Finding],
    ) -> str:
        """Fix an existing docstring."""
        # Determine if we need to fix or enhance
        has_parse_errors = any(f.rule_id == "DG201" for f in findings)
        has_missing_params = any(f.rule_id == "DG202" for f in findings)
        has_extra_params = any(f.rule_id == "DG203" for f in findings)

        if has_parse_errors or has_missing_params or has_extra_params:
            # Use fix strategy
            issues = [f.message for f in findings]
            return self.llm_client.fix_docstring(
                function_signature=context.signature,
                current_docstring=current_docstring,
                issues="; ".join(issues),
            )
        else:
            # Use enhancement strategy
            missing_elements = [f.message for f in findings]
            return self.llm_client.enhance_docstring(
                function_signature=context.signature,
                current_docstring=current_docstring,
                missing_elements="; ".join(missing_elements),
            )

    def _extract_purpose_from_findings(self, findings: List[Finding]) -> str:
        """Extract function purpose from findings or use default."""
        # For now, use a generic purpose
        # In the future, we could analyze the function body or use heuristics
        return "Function implementation"

    def _build_context_from_findings(self, findings: List[Finding]) -> str:
        """Build context string from findings."""
        context_parts = []

        for finding in findings:
            if finding.rule_id == "DG202":
                context_parts.append(f"Missing parameter documentation")
            elif finding.rule_id == "DG203":
                context_parts.append(f"Extra parameter in documentation")
            elif finding.rule_id == "DG204":
                context_parts.append(f"Returns section issue")
            elif finding.rule_id == "DG205":
                context_parts.append(f"Raises section issue")

        return "; ".join(context_parts) if context_parts else ""

    def remediate_file(
        self,
        file_path: Path,
        symbols: List[PythonSymbol],
        findings: List[Finding],
    ) -> List[DocstringChange]:
        """Remediate all symbols in a file."""
        changes = []

        for symbol in symbols:
            if symbol.kind not in {"function", "class"}:
                continue

            change = self.remediate_symbol(symbol, findings, file_path)
            if change:
                changes.append(change)
                self.change_tracker.add_change(change)

                # Check max changes limit
                if (
                    self.options.max_changes
                    and len(self.change_tracker.changes) >= self.options.max_changes
                ):
                    break

        return changes

    def get_summary(self) -> str:
        """Get a summary of all changes."""
        return self.change_tracker.get_summary()

    def get_changes(self) -> List[DocstringChange]:
        """Get all tracked changes."""
        return self.change_tracker.changes.copy()

    def clear_changes(self) -> None:
        """Clear all tracked changes."""
        self.change_tracker.clear()
