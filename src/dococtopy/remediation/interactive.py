"""Interactive review system for docstring fixes.

This module provides an interactive interface for reviewing and approving
LLM-generated docstring fixes with diff previews and user confirmation.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.text import Text

from dococtopy.remediation.diff import DocstringChange


@dataclass
class InteractiveReviewOptions:
    """Options for interactive review."""

    show_full_context: bool = True
    auto_accept_safe_changes: bool = False
    batch_mode: bool = False
    preview_mode: bool = True


class InteractiveReviewer:
    """Interactive reviewer for docstring changes."""

    def __init__(self, console: Console, options: InteractiveReviewOptions):
        self.console = console
        self.options = options
        self.approved_changes: List[DocstringChange] = []
        self.rejected_changes: List[DocstringChange] = []

    def review_changes(
        self, changes: List[DocstringChange], file_path: Path, original_content: str
    ) -> List[DocstringChange]:
        """Review a list of changes interactively."""

        if not changes:
            return []

        self.console.print(
            f"\n[bold blue]Reviewing {len(changes)} changes in {file_path}[/bold blue]"
        )

        approved = []

        for i, change in enumerate(changes, 1):
            self.console.print(f"\n[bold cyan]Change {i}/{len(changes)}[/bold cyan]")

            # Show change details
            self._show_change_details(change)

            # Show diff
            if self.options.preview_mode:
                self._show_diff(change, original_content, file_path)

            # Get user decision
            if self.options.batch_mode:
                decision = self._batch_review(change)
            else:
                decision = self._interactive_review(change)

            if decision == "accept":
                approved.append(change)
                self.approved_changes.append(change)
                self.console.print("[green]✓ Change approved[/green]")
            elif decision == "reject":
                self.rejected_changes.append(change)
                self.console.print("[red]✗ Change rejected[/red]")
            elif decision == "skip":
                self.console.print("[yellow]⏭ Change skipped[/yellow]")
            elif decision == "quit":
                self.console.print("[yellow]Stopping review process[/yellow]")
                break

        return approved

    def _show_change_details(self, change: DocstringChange) -> None:
        """Show details about a specific change."""

        # Symbol info
        symbol_info = Text()
        symbol_info.append("Symbol: ", style="bold")
        symbol_info.append(f"{change.symbol_name} ({change.symbol_kind})", style="cyan")

        # Issues addressed
        issues_info = Text()
        issues_info.append("Issues: ", style="bold")
        issues_info.append(", ".join(change.issues_addressed), style="yellow")

        # Change type
        change_type = Text()
        change_type.append("Type: ", style="bold")
        if change.original_docstring is None:
            change_type.append("Add docstring", style="green")
        elif change.new_docstring is None:
            change_type.append("Remove docstring", style="red")
        else:
            change_type.append("Update docstring", style="blue")

        # Create panel
        content = Text()
        content.append(symbol_info)
        content.append("\n")
        content.append(issues_info)
        content.append("\n")
        content.append(change_type)

        panel = Panel(content, title="Change Details", border_style="blue")

        self.console.print(panel)

    def _show_diff(
        self, change: DocstringChange, original_content: str, file_path: Path
    ) -> None:
        """Show a diff of the change."""

        if not change.original_docstring and not change.new_docstring:
            return

        # Create before/after content
        lines = original_content.splitlines()

        # Find the symbol's line range
        start_line = change.line_number - 1  # Convert to 0-based
        end_line = start_line

        # Find the end of the symbol (rough approximation)
        for i in range(start_line, len(lines)):
            if lines[i].strip() and not lines[i].startswith((" ", "\t")):
                if i > start_line:
                    end_line = i - 1
                    break

        # Create before content
        before_lines = lines[start_line : end_line + 1]
        before_content = "\n".join(before_lines)

        # Create after content by applying the change
        after_lines = before_lines.copy()

        # Apply docstring change
        if (
            change.original_docstring is None or change.original_docstring == ""
        ) and change.new_docstring:
            # Add docstring
            indent = "    "  # Default indentation
            docstring_lines = change.new_docstring.splitlines()
            docstring_content = f'{indent}"""{docstring_lines[0]}\n'
            for line in docstring_lines[1:]:
                docstring_content += f"{indent}{line}\n"
            docstring_content += f'{indent}"""'

            # Insert after function/class definition (at the end of the slice)
            after_lines.append(docstring_content)
        elif change.original_docstring and change.new_docstring:
            # Replace docstring
            for i, line in enumerate(after_lines):
                if '"""' in line and change.original_docstring in line:
                    # Replace the line
                    indent = len(line) - len(line.lstrip())
                    new_docstring = change.new_docstring.replace(
                        "\n", f'\n{" " * indent}'
                    )
                    after_lines[i] = f'{" " * indent}"""{new_docstring}"""'
                    break

        after_content = "\n".join(after_lines)

        # Create diff
        diff = list(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=f"{file_path.name} (before)",
                tofile=f"{file_path.name} (after)",
                lineterm="",
            )
        )

        if diff:
            diff_text = "\n".join(diff)
            syntax = Syntax(diff_text, "diff", theme="monokai")

            panel = Panel(syntax, title="Diff Preview", border_style="green")

            self.console.print(panel)
        else:
            # Fallback: show before/after content if no diff
            self.console.print("\n[bold]Before:[/bold]")
            before_syntax = Syntax(before_content, "python", theme="monokai")
            self.console.print(before_syntax)

            self.console.print("\n[bold]After:[/bold]")
            after_syntax = Syntax(after_content, "python", theme="monokai")
            self.console.print(after_syntax)

    def _interactive_review(self, change: DocstringChange) -> str:
        """Get user decision for a single change."""

        # Show options
        self.console.print("\n[bold]What would you like to do?[/bold]")
        self.console.print("[green]a[/green] - Accept this change")
        self.console.print("[red]r[/red] - Reject this change")
        self.console.print("[yellow]s[/yellow] - Skip this change")
        self.console.print("[blue]p[/blue] - Preview full file with this change")
        self.console.print("[magenta]q[/magenta] - Quit review process")

        while True:
            choice = Prompt.ask(
                "Your choice", choices=["a", "r", "s", "p", "q"], default="a"
            )

            if choice == "a":
                return "accept"
            elif choice == "r":
                return "reject"
            elif choice == "s":
                return "skip"
            elif choice == "p":
                self._preview_full_file(change)
                continue
            elif choice == "q":
                return "quit"

    def _batch_review(self, change: DocstringChange) -> str:
        """Review changes in batch mode."""

        # Auto-accept safe changes
        if self.options.auto_accept_safe_changes and self._is_safe_change(change):
            return "accept"

        # Show batch options
        return (
            Confirm.ask(f"Accept change for {change.symbol_name}?", default=True)
            and "accept"
            or "reject"
        )

    def _is_safe_change(self, change: DocstringChange) -> bool:
        """Determine if a change is safe to auto-accept."""

        # Safe changes: adding docstrings to functions without them
        if (
            change.original_docstring is None
            and change.new_docstring
            and change.symbol_kind == "function"
        ):
            return True

        # Safe changes: fixing simple formatting issues
        if (
            change.original_docstring
            and change.new_docstring
            and len(change.issues_addressed) == 1
            and "DG301" in change.issues_addressed
        ):  # Missing period
            return True

        return False

    def _preview_full_file(self, change: DocstringChange) -> None:
        """Preview the full file with the change applied."""

        # This would show the entire file with syntax highlighting
        # and the change applied
        self.console.print("[yellow]Full file preview not yet implemented[/yellow]")

    def show_summary(self) -> None:
        """Show a summary of the review process."""

        total = len(self.approved_changes) + len(self.rejected_changes)

        if total == 0:
            return

        summary = Text()
        summary.append(f"Review Summary:\n", style="bold")
        summary.append(f"✓ Approved: {len(self.approved_changes)}\n", style="green")
        summary.append(f"✗ Rejected: {len(self.rejected_changes)}\n", style="red")
        summary.append(f"Total reviewed: {total}", style="blue")

        panel = Panel(summary, title="Review Complete", border_style="green")

        self.console.print(panel)
