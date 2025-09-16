from pathlib import Path

from dococtopy.adapters.python.adapter import load_symbols_from_file
from dococtopy.rules.python_rules import (
    DG201GoogleStyleParseError,
    DG202ParamMissingFromDocstring,
    DG203ExtraParamInDocstring,
    DG204ReturnsSectionMissing,
    DG205RaisesSectionValidation,
)


def test_dg201_google_style_parse_error(tmp_path: Path) -> None:
    """Test DG201 detects Google style parse errors."""
    # Valid Google style docstring
    valid_code = '''def func():
    """Summary.

    Args:
        param: Description.
    """
    pass
'''

    # Invalid Google style docstring (missing colon after parameter name)
    invalid_code = '''def func():
    """Summary.

    Args:
        param Description.
    """
    pass
'''

    # Test valid docstring - should not trigger DG201
    p = tmp_path / "valid.py"
    p.write_text(valid_code)
    syms = load_symbols_from_file(p)
    findings = DG201GoogleStyleParseError().check(symbols=syms)
    assert not any(f.rule_id == "DG201" for f in findings)

    # Test invalid docstring - should trigger DG201
    p = tmp_path / "invalid.py"
    p.write_text(invalid_code)
    syms = load_symbols_from_file(p)
    findings = DG201GoogleStyleParseError().check(symbols=syms)
    assert any(f.rule_id == "DG201" for f in findings)
    assert "Google style docstring parse error" in findings[0].message


def test_dg202_param_missing_from_docstring(tmp_path: Path) -> None:
    """Test DG202 detects missing parameters in docstring."""
    code = '''def func(param1, param2):
    """Summary.

    Args:
        param1: Description of param1.
    """
    pass
'''
    p = tmp_path / "test.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    findings = DG202ParamMissingFromDocstring().check(symbols=syms)
    assert any(f.rule_id == "DG202" for f in findings)
    assert "Parameter 'param2' missing from docstring" in findings[0].message


def test_dg203_extra_param_in_docstring(tmp_path: Path) -> None:
    """Test DG203 detects extra parameters in docstring."""
    code = '''def func(param1):
    """Summary.

    Args:
        param1: Description of param1.
        param2: Description of param2.
    """
    pass
'''
    p = tmp_path / "test.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    findings = DG203ExtraParamInDocstring().check(symbols=syms)
    assert any(f.rule_id == "DG203" for f in findings)
    assert "Extra parameter 'param2' in docstring" in findings[0].message


def test_dg204_returns_section_missing(tmp_path: Path) -> None:
    """Test DG204 detects missing Returns section."""
    # Function with return annotation but no Returns section
    code1 = '''def func() -> int:
    """Summary."""
    return 42
'''

    # Function with Returns section but no return annotation
    code2 = '''def func():
    """Summary.

    Returns:
        int: Description.
    """
    return 42
'''

    # Test missing Returns section
    p = tmp_path / "test1.py"
    p.write_text(code1)
    syms = load_symbols_from_file(p)
    findings = DG204ReturnsSectionMissing().check(symbols=syms)
    assert any(f.rule_id == "DG204" for f in findings)
    assert "missing Returns section" in findings[0].message

    # Test missing return annotation
    p = tmp_path / "test2.py"
    p.write_text(code2)
    syms = load_symbols_from_file(p)
    findings = DG204ReturnsSectionMissing().check(symbols=syms)
    assert any(f.rule_id == "DG204" for f in findings)
    assert "no return annotation" in findings[0].message


def test_dg205_raises_section_validation(tmp_path: Path) -> None:
    """Test DG205 detects documented but not raised exceptions."""
    code = '''def func():
    """Summary.

    Raises:
        ValueError: When something goes wrong.
    """
    pass  # No ValueError actually raised
'''
    p = tmp_path / "test.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)
    findings = DG205RaisesSectionValidation().check(symbols=syms)
    assert any(f.rule_id == "DG205" for f in findings)
    assert (
        "Exception 'ValueError' documented in Raises but not raised"
        in findings[0].message
    )


def test_google_rules_skip_methods_without_docstrings(tmp_path: Path) -> None:
    """Test that Google style rules skip functions without docstrings."""
    code = '''def func_without_docstring(param1, param2):
    pass

def func_with_docstring(param1, param2):
    """Summary.

    Args:
        param1: Description.
    """
    pass
'''
    p = tmp_path / "test.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)

    # DG202 should not trigger for function without docstring
    findings = DG202ParamMissingFromDocstring().check(symbols=syms)
    func_without_docstring_findings = [
        f for f in findings if "func_without_docstring" in f.message
    ]
    assert len(func_without_docstring_findings) == 0

    # DG202 should trigger for function with docstring but missing params
    func_with_docstring_findings = [
        f for f in findings if f.symbol == "func_with_docstring"
    ]
    assert len(func_with_docstring_findings) > 0


def test_google_rules_handle_self_parameter(tmp_path: Path) -> None:
    """Test that Google style rules properly handle 'self' parameter."""
    code = '''class MyClass:
    def method(self, param1):
        """Summary.

        Args:
            param1: Description.
        """
        pass
'''
    p = tmp_path / "test.py"
    p.write_text(code)
    syms = load_symbols_from_file(p)

    # Should not complain about missing 'self' parameter
    findings = DG202ParamMissingFromDocstring().check(symbols=syms)
    assert not any("self" in f.message for f in findings)

    # Should not complain about extra 'self' parameter
    findings = DG203ExtraParamInDocstring().check(symbols=syms)
    assert not any("self" in f.message for f in findings)
