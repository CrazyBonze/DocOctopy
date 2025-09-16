"""
Real-world docstring patterns tests based on TinyDB analysis.

These tests are based on actual issues found when scanning the TinyDB codebase
and help ensure our rules catch common real-world docstring problems.
"""

import ast
from pathlib import Path

import pytest

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.rules.python_rules import (
    DG101MissingDocstring,
    DG202ParamMissingFromDocstring,
    DG204ReturnsSectionMissing,
    DG210DocstringIndentation,
    DG301SummaryStyle,
)


class TestRealWorldPatterns:
    """Test patterns found in real-world codebases like TinyDB."""

    def test_simple_utility_function_missing_docstring(self):
        """Test DG101: Simple utility functions often missing docstrings."""
        code = """
def is_sequence(obj):
    return hasattr(obj, '__iter__')
"""
        symbols = self._parse_symbols(code)
        rule = DG101MissingDocstring()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG101"
        assert "is_sequence" in findings[0].message
        assert "missing a docstring" in findings[0].message

    def test_class_missing_docstring(self):
        """Test DG101: Classes missing docstrings."""
        code = """
class TinyDBPlugin:
    def __init__(self):
        pass
"""
        symbols = self._parse_symbols(code)
        rule = DG101MissingDocstring()
        findings = rule.check(symbols=symbols)

        # Should find both the class and __init__ method missing docstrings
        assert len(findings) == 2
        finding_symbols = [f.symbol for f in findings]
        assert "TinyDBPlugin" in finding_symbols
        assert "__init__" in finding_symbols

    def test_operations_functions_missing_parameters(self):
        """Test DG202: Operations-style functions missing parameter docs."""
        code = '''
def delete(field):
    """
    Delete a given field from the document.
    """
    def transform(doc):
        del doc[field]
    return transform
'''
        symbols = self._parse_symbols(code)
        rule = DG202ParamMissingFromDocstring()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG202"
        assert "field" in findings[0].message
        assert "missing from docstring" in findings[0].message

    def test_multiple_parameters_missing(self):
        """Test DG202: Functions with multiple missing parameters."""
        code = '''
def add(field, n):
    """
    Add something to a field.
    """
    def transform(doc):
        doc[field] += n
    return transform
'''
        symbols = self._parse_symbols(code)
        rule = DG202ParamMissingFromDocstring()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 2
        finding_params = [f.message for f in findings]
        assert any("field" in msg for msg in finding_params)
        assert any("n" in msg for msg in finding_params)

    def test_return_annotation_without_returns_section(self):
        """Test DG204: Functions with return annotations but no Returns section."""
        code = '''
def where(key: str) -> Query:
    """
    A shorthand for Query()[key]
    """
    return Query()[key]
'''
        symbols = self._parse_symbols(code)
        rule = DG204ReturnsSectionMissing()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG204"
        assert "return annotation" in findings[0].message
        assert "missing Returns section" in findings[0].message

    def test_docstring_without_period(self):
        """Test DG301: Docstrings missing periods in summary."""
        code = '''
def with_typehint(baseclass):
    """
    Add type hints from a specified class to a base class
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG301SummaryStyle()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG301"
        assert "period" in findings[0].message

    def test_rst_style_docstring_indentation(self):
        """Test DG210: RST-style docstrings with indentation issues."""
        code = '''
class Database:
    """
    A database that stores data in a JSON file.

    When creating a new instance, all arguments and keyword arguments (except
    for ``storage``) will be passed to the storage class that is provided. If
    no storage class is specified, :class:`~tinydb.storages.JSONStorage` will be
    used.

    .. admonition:: Customization

        For customization, the following class variables can be set:

        - ``table_class`` defines the class that is used to create tables,
        - ``default_table_name`` defines the name of the default table, and
        - ``default_storage_class`` will define the class that will be used to
          create storage instances if no other storage is passed.
    """
    pass
'''
        symbols = self._parse_symbols(code)
        rule = DG210DocstringIndentation()
        findings = rule.check(symbols=symbols)

        # This should detect the inconsistent indentation in the RST sections
        assert len(findings) >= 1
        assert findings[0].rule_id == "DG210"
        assert "Inconsistent indentation" in findings[0].message

    def test_protocol_class_with_detailed_docstring(self):
        """Test that detailed protocol docstrings pass validation."""
        code = '''
class QueryLike(Protocol):
    """
    A typing protocol that acts like a query.

    Something that we use as a query must have two properties:

    1. It must be callable, accepting a `Mapping` object and returning a
       boolean that indicates whether the value matches the query, and
    2. it must have a stable hash that will be used for query caching.

    In addition, to mark a query as non-cacheable (e.g. if it involves
    some remote lookup) it needs to have a method called ``is_cacheable``
    that returns ``False``.

    This query protocol is used to make MyPy correctly support the query
    pattern that TinyDB uses.

    See also https://mypy.readthedocs.io/en/stable/protocols.html#simple-user-defined-protocols
    """
    def __call__(self, value: Mapping) -> bool: ...
    def __hash__(self) -> int: ...
'''
        symbols = self._parse_symbols(code)

        # Test multiple rules to ensure this well-formatted docstring passes
        rules = [
            DG301SummaryStyle(),
        ]

        for rule in rules:
            findings = rule.check(symbols=symbols)
            assert len(findings) == 0, f"Rule {rule.id} failed: {findings}"

        # DG210 should detect indentation issues in this realistic docstring
        rule = DG210DocstringIndentation()
        findings = rule.check(symbols=symbols)
        assert (
            len(findings) >= 1
        ), "Should detect indentation issues in real-world docstring"
        assert findings[0].rule_id == "DG210"

        # For DG101, we expect the class to pass but the abstract methods to fail
        # This is realistic behavior for Protocol classes
        rule = DG101MissingDocstring()
        findings = rule.check(symbols=symbols)
        # Should find the abstract methods missing docstrings, but not the class
        assert len(findings) == 2
        finding_symbols = [f.symbol for f in findings]
        assert "__call__" in finding_symbols
        assert "__hash__" in finding_symbols
        assert "QueryLike" not in finding_symbols

    def test_factory_function_with_missing_params(self):
        """Test DG202: Factory functions missing parameter documentation."""
        code = '''
def create_storage(path, create_dirs=True):
    """
    Create a new storage instance.
    """
    return JSONStorage(path)
'''
        symbols = self._parse_symbols(code)
        rule = DG202ParamMissingFromDocstring()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 2
        finding_params = [f.message for f in findings]
        assert any("path" in msg for msg in finding_params)
        assert any("create_dirs" in msg for msg in finding_params)

    def test_decorator_function_missing_docstring(self):
        """Test DG101: Decorator functions often missing docstrings."""
        code = """
def plugin(func):
    return func
"""
        symbols = self._parse_symbols(code)
        rule = DG101MissingDocstring()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG101"
        assert "plugin" in findings[0].message

    def test_nested_function_with_docstring(self):
        """Test that nested functions with docstrings are handled correctly."""
        code = '''
def outer_function():
    """
    Outer function with proper docstring.
    """
    def inner_function():
        """
        Inner function with proper docstring.
        """
        pass
    return inner_function
'''
        symbols = self._parse_symbols(code)

        # Should find both functions
        assert len(symbols) == 2

        # Both should pass docstring validation
        rule = DG101MissingDocstring()
        findings = rule.check(symbols=symbols)
        assert len(findings) == 0

    def test_class_method_with_missing_params(self):
        """Test DG202: Class methods missing parameter documentation."""
        code = '''
class MyClass:
    def method(self, param1, param2):
        """
        A method that does something.
        """
        pass
'''
        symbols = self._parse_symbols(code)
        rule = DG202ParamMissingFromDocstring()
        findings = rule.check(symbols=symbols)

        # Should find missing param1 and param2, but not self
        assert len(findings) == 2
        finding_params = [f.message for f in findings]
        assert any("param1" in msg for msg in finding_params)
        assert any("param2" in msg for msg in finding_params)
        assert not any("self" in msg for msg in finding_params)

    def test_static_method_with_return_annotation(self):
        """Test DG204: Static methods with return annotations."""
        code = '''
class MyClass:
    @staticmethod
    def static_method(value: int) -> str:
        """
        A static method that converts int to str.
        """
        return str(value)
'''
        symbols = self._parse_symbols(code)
        rule = DG204ReturnsSectionMissing()
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG204"

    def _parse_symbols(self, code: str) -> list[PythonSymbol]:
        """Parse code and return PythonSymbol objects."""
        tree = ast.parse(code)
        symbols = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                symbols.append(
                    PythonSymbol(
                        name=node.name,
                        kind=(
                            "function" if isinstance(node, ast.FunctionDef) else "class"
                        ),
                        docstring=docstring,
                        lineno=node.lineno,
                        col=node.col_offset,
                        ast_node=node,
                    )
                )

        return symbols
