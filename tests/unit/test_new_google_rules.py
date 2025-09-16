"""
Unit tests for new Google-style docstring rules (DG206-DG210).
"""

import ast
from pathlib import Path

import pytest

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.rules.python_rules import (
    DG206ArgsSectionFormat,
    DG207ReturnsSectionFormat,
    DG208RaisesSectionFormat,
    DG209SummaryLength,
    DG210DocstringIndentation,
)


class TestDG206ArgsSectionFormat:
    """Test DG206: Args section format validation."""

    def test_args_section_missing_description(self):
        """Test detection of missing parameter descriptions."""
        code = '''
def example_func(param1, param2):
    """Example function.
    
    Args:
        param1: 
        param2: Description for param2.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG206ArgsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG206"
        assert "param1" in findings[0].message
        assert "missing description" in findings[0].message

    def test_args_section_lowercase_description(self):
        """Test detection of lowercase parameter descriptions."""
        code = '''
def example_func(param1):
    """Example function.
    
    Args:
        param1: this should be capitalized.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG206ArgsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG206"
        assert "param1" in findings[0].message
        assert "capital letter" in findings[0].message

    def test_args_section_proper_format(self):
        """Test that properly formatted Args sections pass."""
        code = '''
def example_func(param1, param2):
    """Example function.
    
    Args:
        param1: Proper description for param1.
        param2: Another proper description.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG206ArgsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_no_args_section(self):
        """Test that functions without Args sections pass."""
        code = '''
def example_func():
    """Example function without parameters."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG206ArgsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def _parse_symbols(self, code: str) -> list[PythonSymbol]:
        """Parse code and return PythonSymbol objects."""
        tree = ast.parse(code)
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind="function",
                        docstring=docstring,
                        lineno=node.lineno,
                        col=node.col_offset,
                        ast_node=node,
                    )
                )

        return symbols


class TestDG207ReturnsSectionFormat:
    """Test DG207: Returns section format validation."""

    def test_returns_section_missing_description(self):
        """Test detection of missing Returns description."""
        code = '''
def example_func():
    """Example function.
    
    Returns:
        
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG207ReturnsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG207"
        assert "missing description" in findings[0].message

    def test_returns_section_lowercase_description(self):
        """Test detection of lowercase Returns description."""
        code = '''
def example_func():
    """Example function.
    
    Returns:
        some value.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG207ReturnsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG207"
        assert "capital letter" in findings[0].message

    def test_returns_section_proper_format(self):
        """Test that properly formatted Returns sections pass."""
        code = '''
def example_func():
    """Example function.
    
    Returns:
        Some value that is returned.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG207ReturnsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_no_returns_section(self):
        """Test that functions without Returns sections pass."""
        code = '''
def example_func():
    """Example function without return."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG207ReturnsSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def _parse_symbols(self, code: str) -> list[PythonSymbol]:
        """Parse code and return PythonSymbol objects."""
        tree = ast.parse(code)
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind="function",
                        docstring=docstring,
                        lineno=node.lineno,
                        col=node.col_offset,
                        ast_node=node,
                    )
                )

        return symbols


class TestDG208RaisesSectionFormat:
    """Test DG208: Raises section format validation."""

    def test_raises_section_missing_description(self):
        """Test detection of missing Raises descriptions."""
        code = '''
def example_func():
    """Example function.
    
    Raises:
        ValueError: 
        TypeError: Some description.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG208RaisesSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG208"
        assert "ValueError" in findings[0].message
        assert "missing description" in findings[0].message

    def test_raises_section_lowercase_description(self):
        """Test detection of lowercase Raises descriptions."""
        code = '''
def example_func():
    """Example function.
    
    Raises:
        ValueError: this should be capitalized.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG208RaisesSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG208"
        assert "ValueError" in findings[0].message
        assert "capital letter" in findings[0].message

    def test_raises_section_proper_format(self):
        """Test that properly formatted Raises sections pass."""
        code = '''
def example_func():
    """Example function.
    
    Raises:
        ValueError: When invalid input is provided.
        TypeError: When wrong type is passed.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG208RaisesSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_no_raises_section(self):
        """Test that functions without Raises sections pass."""
        code = '''
def example_func():
    """Example function without exceptions."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG208RaisesSectionFormat()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def _parse_symbols(self, code: str) -> list[PythonSymbol]:
        """Parse code and return PythonSymbol objects."""
        tree = ast.parse(code)
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind="function",
                        docstring=docstring,
                        lineno=node.lineno,
                        col=node.col_offset,
                        ast_node=node,
                    )
                )

        return symbols


class TestDG209SummaryLength:
    """Test DG209: Summary length validation."""

    def test_summary_too_short(self):
        """Test detection of too short summaries."""
        code = '''
def example_func():
    """Short."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG209SummaryLength()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG209"
        assert "too short" in findings[0].message

    def test_summary_too_long(self):
        """Test detection of too long summaries."""
        code = '''
def example_func():
    """This is a very long summary that exceeds the recommended length of eighty characters and should trigger the warning."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG209SummaryLength()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG209"
        assert "too long" in findings[0].message

    def test_summary_appropriate_length(self):
        """Test that appropriately sized summaries pass."""
        code = '''
def example_func():
    """This is a good summary of appropriate length."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG209SummaryLength()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_no_summary(self):
        """Test that functions without summaries pass."""
        code = '''
def example_func():
    """
    Args:
        param1: Description.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG209SummaryLength()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def _parse_symbols(self, code: str) -> list[PythonSymbol]:
        """Parse code and return PythonSymbol objects."""
        tree = ast.parse(code)
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind="function",
                        docstring=docstring,
                        lineno=node.lineno,
                        col=node.col_offset,
                        ast_node=node,
                    )
                )

        return symbols


class TestDG210DocstringIndentation:
    """Test DG210: Docstring indentation validation."""

    def test_inconsistent_indentation(self):
        """Test detection of inconsistent indentation."""
        code = '''
def example_func():
    """Example function.
    
    This line has proper indentation.
        This line has too much indentation.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG210DocstringIndentation()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG210"
        assert "Inconsistent indentation" in findings[0].message

    def test_consistent_indentation(self):
        """Test that consistently indented docstrings pass."""
        code = '''
def example_func():
    """Example function.
    
    This line has proper indentation.
    This line also has proper indentation.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG210DocstringIndentation()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_single_line_docstring(self):
        """Test that single-line docstrings pass."""
        code = '''
def example_func():
    """Single line docstring."""
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG210DocstringIndentation()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_no_docstring(self):
        """Test that functions without docstrings pass."""
        code = """
def example_func():
    pass
"""
        symbols = self._parse_symbols(code)
        rule = DG210DocstringIndentation()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def _parse_symbols(self, code: str) -> list[PythonSymbol]:
        """Parse code and return PythonSymbol objects."""
        tree = ast.parse(code)
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind="function",
                        docstring=docstring,
                        lineno=node.lineno,
                        col=node.col_offset,
                        ast_node=node,
                    )
                )

        return symbols
