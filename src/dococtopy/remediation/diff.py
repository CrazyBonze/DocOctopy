"""Diff generator for showing docstring changes.

This module provides utilities for generating and displaying
differences between original and modified docstrings.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DocstringChange:
    """Represents a change to a docstring."""

    symbol_name: str
    symbol_kind: str
    file_path: str
    line_number: int
    original_docstring: str
    new_docstring: str
    change_type: str  # "added", "modified", "enhanced"
    issues_addressed: List[str]


class DiffGenerator:
    """Generates diffs for docstring changes."""

    @staticmethod
    def generate_unified_diff(change: DocstringChange, context_lines: int = 3) -> str:
        """Generate a unified diff for a docstring change."""
        # Prepare the original and new content
        original_lines = change.original_docstring.splitlines(keepends=True)
        new_lines = change.new_docstring.splitlines(keepends=True)

        # Generate unified diff
        diff = difflib.unified_diff(
            original_lines,
            new_lines,
            fromfile=f"{change.file_path}:{change.line_number} (original)",
            tofile=f"{change.file_path}:{change.line_number} (modified)",
            lineterm="",
            n=context_lines,
        )

        return "\n".join(diff)

    @staticmethod
    def generate_context_diff(change: DocstringChange, context_lines: int = 3) -> str:
        """Generate a context diff for a docstring change."""
        original_lines = change.original_docstring.splitlines(keepends=True)
        new_lines = change.new_docstring.splitlines(keepends=True)

        diff = difflib.context_diff(
            original_lines,
            new_lines,
            fromfile=f"{change.file_path}:{change.line_number} (original)",
            tofile=f"{change.file_path}:{change.line_number} (modified)",
            lineterm="",
            n=context_lines,
        )

        return "\n".join(diff)

    @staticmethod
    def generate_side_by_side_diff(change: DocstringChange, width: int = 80) -> str:
        """Generate a side-by-side diff for a docstring change."""
        original_lines = change.original_docstring.splitlines()
        new_lines = change.new_docstring.splitlines()

        # Use difflib's HtmlDiff for side-by-side comparison
        differ = difflib.HtmlDiff(wrapcolumn=width)
        html_diff = differ.make_table(
            original_lines,
            new_lines,
            fromdesc=f"{change.file_path}:{change.line_number} (original)",
            todesc=f"{change.file_path}:{change.line_number} (modified)",
        )

        return html_diff

    @staticmethod
    def generate_simple_diff(change: DocstringChange) -> str:
        """Generate a simple before/after diff."""
        lines = [
            f"--- {change.file_path}:{change.line_number} ({change.symbol_name})",
            f"+++ {change.file_path}:{change.line_number} ({change.symbol_name})",
            "",
            "Original docstring:",
            '"""',
            change.original_docstring,
            '"""',
            "",
            "New docstring:",
            '"""',
            change.new_docstring,
            '"""',
            "",
            f"Issues addressed: {', '.join(change.issues_addressed)}",
        ]

        return "\n".join(lines)

    @staticmethod
    def generate_summary(changes: List[DocstringChange]) -> str:
        """Generate a summary of all changes."""
        if not changes:
            return "No changes to apply."

        summary_lines = [
            f"Docstring Changes Summary",
            f"=" * 50,
            f"",
            f"Total changes: {len(changes)}",
            f"",
        ]

        # Group by change type
        by_type = {}
        for change in changes:
            if change.change_type not in by_type:
                by_type[change.change_type] = []
            by_type[change.change_type].append(change)

        for change_type, change_list in by_type.items():
            summary_lines.extend(
                [
                    f"{change_type.capitalize()} ({len(change_list)}):",
                ]
            )
            for change in change_list:
                summary_lines.append(
                    f"  - {change.file_path}:{change.line_number} ({change.symbol_name})"
                )
            summary_lines.append("")

        return "\n".join(summary_lines)

    @staticmethod
    def format_change_for_display(
        change: DocstringChange, format_type: str = "unified"
    ) -> str:
        """Format a change for display based on the specified format."""
        if format_type == "unified":
            return DiffGenerator.generate_unified_diff(change)
        elif format_type == "context":
            return DiffGenerator.generate_context_diff(change)
        elif format_type == "side_by_side":
            return DiffGenerator.generate_side_by_side_diff(change)
        elif format_type == "simple":
            return DiffGenerator.generate_simple_diff(change)
        else:
            raise ValueError(f"Unknown format type: {format_type}")


class ChangeTracker:
    """Tracks and manages docstring changes."""

    def __init__(self):
        self.changes: List[DocstringChange] = []

    def add_change(self, change: DocstringChange) -> None:
        """Add a change to the tracker."""
        self.changes.append(change)

    def get_changes_for_file(self, file_path: str) -> List[DocstringChange]:
        """Get all changes for a specific file."""
        return [c for c in self.changes if c.file_path == file_path]

    def get_changes_for_symbol(self, symbol_name: str) -> List[DocstringChange]:
        """Get all changes for a specific symbol."""
        return [c for c in self.changes if c.symbol_name == symbol_name]

    def clear(self) -> None:
        """Clear all tracked changes."""
        self.changes.clear()

    def has_changes(self) -> bool:
        """Check if there are any tracked changes."""
        return len(self.changes) > 0

    def get_summary(self) -> str:
        """Get a summary of all changes."""
        return DiffGenerator.generate_summary(self.changes)
