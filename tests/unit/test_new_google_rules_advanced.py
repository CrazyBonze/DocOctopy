"""Unit tests for new Google style docstring rules (DG211-DG214)."""

from pathlib import Path

import pytest

from dococtopy.adapters.python.adapter import load_symbols_from_file
from dococtopy.rules.python_rules import (
    DG211YieldsSectionValidation,
    DG212AttributesSectionValidation,
    DG213ExamplesSectionValidation,
    DG214NoteSectionValidation,
)


class TestDG211YieldsSectionValidation:
    """Test DG211: Generator functions should have Yields section."""

    def test_generator_without_yields_section(self, tmp_path: Path):
        """Test generator function without Yields section."""
        rule = DG211YieldsSectionValidation()

        code = '''
def example_generator(n):
    """Generate numbers from 0 to n-1.
    
    Args:
        n (int): The upper limit.
    """
    for i in range(n):
        yield i
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG211"
        assert "Yields section" in findings[0].message

    def test_generator_with_yields_section(self, tmp_path: Path):
        """Test generator function with proper Yields section."""
        rule = DG211YieldsSectionValidation()

        code = '''
def example_generator(n):
    """Generate numbers from 0 to n-1.
    
    Args:
        n (int): The upper limit.
        
    Yields:
        int: The next number in the range.
    """
    for i in range(n):
        yield i
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_non_generator_function(self, tmp_path: Path):
        """Test that non-generator functions are ignored."""
        rule = DG211YieldsSectionValidation()

        code = '''
def regular_function(n):
    """A regular function.
    
    Args:
        n (int): A parameter.
    """
    return n * 2
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0


class TestDG212AttributesSectionValidation:
    """Test DG212: Classes should document public attributes."""

    def test_class_without_attributes_section(self, tmp_path: Path):
        """Test class with public attributes but no Attributes section."""
        rule = DG212AttributesSectionValidation()

        code = '''
class ExampleClass:
    """A class with public attributes.
    
    Args:
        param1 (str): First parameter.
    """
    
    def __init__(self, param1, param2):
        self.attr1 = param1
        self.attr2 = param2
        self._private = "private"
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG212"
        assert "Attributes section" in findings[0].message

    def test_class_with_attributes_section(self, tmp_path: Path):
        """Test class with proper Attributes section."""
        rule = DG212AttributesSectionValidation()

        code = '''
class ExampleClass:
    """A class with public attributes.
    
    Args:
        param1 (str): First parameter.
        
    Attributes:
        attr1 (str): First attribute.
        attr2 (str): Second attribute.
    """
    
    def __init__(self, param1, param2):
        self.attr1 = param1
        self.attr2 = param2
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_class_without_public_attributes(self, tmp_path: Path):
        """Test class without public attributes."""
        rule = DG212AttributesSectionValidation()

        code = '''
class ExampleClass:
    """A class without public attributes."""
    
    def __init__(self):
        self._private = "private"
        self.__very_private = "very private"
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0


class TestDG213ExamplesSectionValidation:
    """Test DG213: Complex functions should have Examples section."""

    def test_complex_function_without_examples(self, tmp_path: Path):
        """Test complex function without Examples section."""
        rule = DG213ExamplesSectionValidation()

        code = '''
def complex_function(param1, param2, param3, param4, param5):
    """A complex function with many parameters.
    
    Args:
        param1 (str): First parameter.
        param2 (int): Second parameter.
        param3 (bool): Third parameter.
        param4 (list): Fourth parameter.
        param5 (dict): Fifth parameter.
        
    Returns:
        str: Result string.
    """
    return f"{param1}-{param2}-{param3}-{param4}-{param5}"
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG213"
        assert "Examples section" in findings[0].message

    def test_complex_function_with_examples(self, tmp_path: Path):
        """Test complex function with proper Examples section."""
        rule = DG213ExamplesSectionValidation()

        code = '''
def complex_function(param1, param2, param3, param4, param5):
    """A complex function with many parameters.
    
    Args:
        param1 (str): First parameter.
        param2 (int): Second parameter.
        param3 (bool): Third parameter.
        param4 (list): Fourth parameter.
        param5 (dict): Fifth parameter.
        
    Returns:
        str: Result string.
        
    Examples:
        >>> result = complex_function("a", 1, True, [], {})
        >>> print(result)
        "a-1-True-[]-{}"
    """
    return f"{param1}-{param2}-{param3}-{param4}-{param5}"
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_simple_function(self, tmp_path: Path):
        """Test that simple functions are ignored."""
        rule = DG213ExamplesSectionValidation()

        code = '''
def simple_function(param):
    """A simple function.
    
    Args:
        param (str): A parameter.
        
    Returns:
        str: Result.
    """
    return param
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0


class TestDG214NoteSectionValidation:
    """Test DG214: Functions with special behavior should have Note sections."""

    def test_function_with_args_kwargs_without_note(self, tmp_path: Path):
        """Test function with *args/**kwargs without Note section."""
        rule = DG214NoteSectionValidation()

        code = '''
def flexible_function(param1, *args, **kwargs):
    """A function that accepts variable arguments.
    
    Args:
        param1 (str): Required parameter.
        *args: Variable length arguments.
        **kwargs: Arbitrary keyword arguments.
        
    Returns:
        str: Result string.
    """
    return f"{param1}-{len(args)}-{len(kwargs)}"
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 1
        assert findings[0].rule_id == "DG214"
        assert "Note section" in findings[0].message

    def test_function_with_args_kwargs_with_note(self, tmp_path: Path):
        """Test function with *args/**kwargs with proper Note section."""
        rule = DG214NoteSectionValidation()

        code = '''
def flexible_function(param1, *args, **kwargs):
    """A function that accepts variable arguments.
    
    Args:
        param1 (str): Required parameter.
        *args: Variable length arguments.
        **kwargs: Arbitrary keyword arguments.
        
    Returns:
        str: Result string.
        
    Note:
        This function accepts variable arguments for flexibility.
    """
    return f"{param1}-{len(args)}-{len(kwargs)}"
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0

    def test_decorated_function_without_note(self, tmp_path: Path):
        """Test decorated function without Note section."""
        rule = DG214NoteSectionValidation()

        code = '''
def decorator(func):
    """A decorator function."""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def decorated_function(param):
    """A decorated function.
    
    Args:
        param (str): A parameter.
        
    Returns:
        str: Result.
    """
    return param
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        # Should find the decorated function
        decorated_findings = [f for f in findings if f.symbol == "decorated_function"]
        assert len(decorated_findings) == 1
        assert decorated_findings[0].rule_id == "DG214"

    def test_regular_function(self, tmp_path: Path):
        """Test that regular functions are ignored."""
        rule = DG214NoteSectionValidation()

        code = '''
def regular_function(param):
    """A regular function.
    
    Args:
        param (str): A parameter.
        
    Returns:
        str: Result.
    """
    return param
'''

        p = tmp_path / "test.py"
        p.write_text(code)
        symbols = load_symbols_from_file(p)
        findings = rule.check(symbols=symbols)

        assert len(findings) == 0
