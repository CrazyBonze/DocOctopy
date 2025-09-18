"""Unit tests for docstring validation and trivial fix detection."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pytest

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.core.findings import Finding, FindingLevel, Location
from dococtopy.remediation.validation import (
    DocstringFixer,
    DocstringValidator,
    TrivialFixDetector,
    ValidationResult,
)


class TestDocstringValidator:
    """Test docstring validation functionality."""

    def test_validate_valid_docstring(self):
        """Test validation of a compliant docstring."""
        validator = DocstringValidator()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="Test function.",
        )

        result = validator.validate_docstring(symbol, symbol.docstring)

        # Should be valid (no findings)
        assert result.is_valid

    def test_validate_missing_docstring(self):
        """Test validation of missing docstring."""
        validator = DocstringValidator()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="",
        )

        result = validator.validate_docstring(symbol, "")

        # Should have DG101 finding
        assert not result.is_valid
        assert len(result.findings) > 0
        assert any(f.rule_id == "DG101" for f in result.findings)

    def test_validate_missing_period(self):
        """Test validation of docstring missing period."""
        validator = DocstringValidator()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="Test function",
        )

        result = validator.validate_docstring(symbol, symbol.docstring)

        # Should have DG301 finding (missing period)
        assert not result.is_valid
        assert any(f.rule_id == "DG301" for f in result.findings)


class TestTrivialFixDetector:
    """Test trivial fix detection and application."""

    def test_fix_summary_period(self):
        """Test fixing missing period in summary."""
        detector = TrivialFixDetector()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="Test function",
        )

        finding = Finding(
            rule_id="DG301",
            level=FindingLevel.WARNING,
            message="Summary first line should end with period",
            symbol="test_func",
            location=Location(line=1, column=0),
        )

        fixed_docstring, applied_fixes = detector.detect_and_fix(symbol, [finding])

        assert fixed_docstring is not None
        assert "Test function." in fixed_docstring
        assert len(applied_fixes) == 1
        assert "DG301" in applied_fixes[0]

    def test_fix_blank_line_after_summary(self):
        """Test fixing missing blank line after summary."""
        detector = TrivialFixDetector()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="Test function.\nArgs:\n    x: Test parameter",
        )

        finding = Finding(
            rule_id="DG302",
            level=FindingLevel.WARNING,
            message="Blank line required after summary",
            symbol="test_func",
            location=Location(line=1, column=0),
        )

        fixed_docstring, applied_fixes = detector.detect_and_fix(symbol, [finding])

        assert fixed_docstring is not None
        assert "Test function.\n\nArgs:" in fixed_docstring
        assert len(applied_fixes) == 1
        assert "DG302" in applied_fixes[0]

    def test_no_trivial_fixes_available(self):
        """Test when no trivial fixes can be applied."""
        detector = TrivialFixDetector()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="",  # Missing docstring - not trivial to fix
        )

        finding = Finding(
            rule_id="DG101",
            level=FindingLevel.ERROR,
            message="Function 'test_func' is missing a docstring",
            symbol="test_func",
            location=Location(line=1, column=0),
        )

        fixed_docstring, applied_fixes = detector.detect_and_fix(symbol, [finding])

        assert fixed_docstring is None
        assert len(applied_fixes) == 0

    def test_multiple_trivial_fixes(self):
        """Test applying multiple trivial fixes."""
        detector = TrivialFixDetector()

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="Test function\nArgs:\n    x: Test parameter",  # Missing period and blank line
        )

        findings = [
            Finding(
                rule_id="DG301",
                level=FindingLevel.WARNING,
                message="Summary first line should end with period",
                symbol="test_func",
                location=Location(line=1, column=0),
            ),
            Finding(
                rule_id="DG302",
                level=FindingLevel.WARNING,
                message="Blank line required after summary",
                symbol="test_func",
                location=Location(line=1, column=0),
            ),
        ]

        fixed_docstring, applied_fixes = detector.detect_and_fix(symbol, findings)

        assert fixed_docstring is not None
        assert "Test function." in fixed_docstring
        assert "Test function.\n\nArgs:" in fixed_docstring
        assert len(applied_fixes) == 2


class TestDocstringFixer:
    """Test the combined docstring fixer."""

    def test_trivial_fixes_only(self):
        """Test when only trivial fixes are needed."""
        validator = DocstringValidator()
        detector = TrivialFixDetector()
        fixer = DocstringFixer(validator, detector)

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="Test function\nArgs:\n    x: Test parameter",
        )

        findings = [
            Finding(
                rule_id="DG301",
                level=FindingLevel.WARNING,
                message="Summary first line should end with period",
                symbol="test_func",
                location=Location(line=1, column=0),
            ),
            Finding(
                rule_id="DG302",
                level=FindingLevel.WARNING,
                message="Blank line required after summary",
                symbol="test_func",
                location=Location(line=1, column=0),
            ),
        ]

        # Mock LLM client (shouldn't be called)
        class MockLLMClient:
            def generate_docstring(self, *args, **kwargs):
                raise AssertionError("LLM should not be called for trivial fixes")

            def fix_docstring(self, *args, **kwargs):
                raise AssertionError("LLM should not be called for trivial fixes")

        mock_llm = MockLLMClient()

        fixed_docstring, applied_fixes, used_llm = fixer.fix_docstring(
            symbol=symbol, original_findings=findings, llm_client=mock_llm
        )

        assert fixed_docstring is not None
        assert "Test function." in fixed_docstring
        assert "Test function.\n\nArgs:" in fixed_docstring
        assert len(applied_fixes) == 2
        assert not used_llm

    def test_llm_fallback_for_complex_fixes(self):
        """Test LLM fallback for complex fixes."""
        validator = DocstringValidator()
        detector = TrivialFixDetector()
        fixer = DocstringFixer(validator, detector)

        symbol = PythonSymbol(
            name="test_func",
            kind="function",
            lineno=1,
            col=0,
            docstring="",  # Missing docstring - requires LLM
        )

        findings = [
            Finding(
                rule_id="DG101",
                level=FindingLevel.ERROR,
                message="Function 'test_func' is missing a docstring",
                symbol="test_func",
                location=Location(line=1, column=0),
            ),
        ]

        # Mock LLM client
        class MockLLMClient:
            def generate_docstring(self, *args, **kwargs):
                return "Test function.\n\nArgs:\n    x: Test parameter\n\nReturns:\n    Test result"

            def fix_docstring(self, *args, **kwargs):
                return "Fixed docstring"

        mock_llm = MockLLMClient()

        fixed_docstring, applied_fixes, used_llm = fixer.fix_docstring(
            symbol=symbol, original_findings=findings, llm_client=mock_llm
        )

        assert fixed_docstring is not None
        assert "Test function." in fixed_docstring
        assert len(applied_fixes) == 1
        assert "LLM fix attempt 1" in applied_fixes[0]
        assert used_llm
