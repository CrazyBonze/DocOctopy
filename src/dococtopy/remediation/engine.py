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
from dococtopy.remediation.validation import (
    DocstringFixer,
    DocstringValidator,
    TrivialFixDetector,
)


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

    def __init__(self, options: RemediationOptions, config=None):
        self.options = options
        self.config = config
        self.llm_client = create_llm_client(
            options.llm_config
            or LLMConfig(
                provider="openai",
                model="gpt-4o-mini",
            )
        )
        self.change_tracker = ChangeTracker()

        # Initialize validation components
        self.validator = DocstringValidator(config)
        self.trivial_detector = TrivialFixDetector()
        self.docstring_fixer = DocstringFixer(self.validator, self.trivial_detector)

    def remediate_symbol(
        self,
        symbol: PythonSymbol,
        findings: List[Finding],
        file_path: Path,
    ) -> Optional[DocstringChange]:
        """Remediate a single symbol's docstring with validation and retry logic."""
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

        # Use the new validation-based fixer
        try:
            new_docstring, applied_fixes, used_llm = self.docstring_fixer.fix_docstring(
                symbol=symbol,
                original_findings=symbol_findings,
                llm_client=self.llm_client,
                file_path=file_path,
            )
        except Exception as e:
            print(f"Warning: Failed to fix docstring for {symbol.name}: {e}")
            return None

        if new_docstring == symbol.docstring:
            return None  # No change needed

        # Determine change type
        change_type = "added" if not symbol.docstring else "modified"

        # Create change record with additional metadata
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

        # Add metadata about fixes applied
        if hasattr(change, "metadata"):
            change.metadata = {
                "applied_fixes": applied_fixes,
                "used_llm": used_llm,
                "fix_count": len(applied_fixes),
            }

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

    def apply_changes(self, file_path: Path, changes: List[DocstringChange]) -> None:
        """Apply approved changes to a file."""
        if not changes:
            return

        # Read original file content
        original_content = file_path.read_text(encoding="utf-8")
        lines = original_content.splitlines()

        # Sort changes by line number (descending) to avoid line number shifts
        sorted_changes = sorted(changes, key=lambda c: c.line_number, reverse=True)

        for change in sorted_changes:
            # Find the symbol's line range
            symbol_line = change.line_number - 1  # Convert to 0-based

            if (
                change.original_docstring is None or change.original_docstring == ""
            ) and change.new_docstring:
                # Add docstring
                indent = "    "  # Default indentation
                docstring_lines = change.new_docstring.splitlines()

                # Create docstring content
                docstring_content = f'{indent}"""{docstring_lines[0]}'
                for line in docstring_lines[1:]:
                    docstring_content += f"\n{indent}{line}"
                docstring_content += f'\n{indent}"""'

                # Insert after function/class definition (line 3 -> index 2)
                # Insert at symbol_line + 1 (after the definition line)
                lines.insert(symbol_line + 1, docstring_content + "\n")

            elif change.original_docstring and change.new_docstring:
                # Replace docstring
                # Find the docstring lines
                start_line = symbol_line
                end_line = start_line

                # Look for the docstring
                for i in range(symbol_line, len(lines)):
                    line = lines[i]
                    if '"""' in line:
                        # Found start of docstring
                        start_line = i
                        # Find end of docstring
                        for j in range(i + 1, len(lines)):
                            if '"""' in lines[j]:
                                end_line = j
                                break
                        break

                # Replace the docstring
                if start_line != end_line:
                    # Multi-line docstring
                    indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                    new_docstring_lines = change.new_docstring.splitlines()

                    # Replace first line
                    lines[start_line] = f'{" " * indent}"""{new_docstring_lines[0]}'

                    # Replace middle lines
                    for i, line in enumerate(new_docstring_lines[1:], 1):
                        if start_line + i <= end_line:
                            lines[start_line + i] = f'{" " * indent}{line}'
                        else:
                            lines.insert(start_line + i, f'{" " * indent}{line}')

                    # Replace last line
                    if start_line + len(new_docstring_lines) <= end_line:
                        lines[start_line + len(new_docstring_lines)] = (
                            f'{" " * indent}"""'
                        )
                    else:
                        lines.insert(
                            start_line + len(new_docstring_lines), f'{" " * indent}"""'
                        )

                    # Remove any remaining old docstring lines
                    if start_line + len(new_docstring_lines) + 1 <= end_line:
                        del lines[
                            start_line + len(new_docstring_lines) + 1 : end_line + 1
                        ]
                else:
                    # Single line docstring
                    indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                    lines[start_line] = f'{" " * indent}"""{change.new_docstring}"""'

        # Write updated content
        updated_content = "\n".join(lines)
        if original_content.endswith("\n"):
            updated_content += "\n"
        file_path.write_text(updated_content, encoding="utf-8")

    def clear_changes(self) -> None:
        """Clear all tracked changes."""
        self.change_tracker.clear()
