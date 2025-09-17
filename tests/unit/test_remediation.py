"""Tests for LLM remediation components."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.core.findings import Finding, FindingLevel, Location
from dococtopy.remediation.diff import ChangeTracker, DiffGenerator, DocstringChange
from dococtopy.remediation.engine import RemediationEngine, RemediationOptions
from dococtopy.remediation.llm import LLMConfig
from dococtopy.remediation.prompts import FunctionContext, PromptBuilder


def test_function_context_building(tmp_path: Path) -> None:
    """Test building function context from Python symbols."""
    # Create a test Python file
    test_code = '''def test_function(param1: int, param2: str) -> bool:
    """Existing docstring."""
    return True
'''

    test_file = tmp_path / "test.py"
    test_file.write_text(test_code)

    # Load symbols
    from dococtopy.adapters.python.adapter import load_symbols_from_file

    symbols = load_symbols_from_file(test_file)

    # Find the function symbol
    func_symbol = next(s for s in symbols if s.name == "test_function")

    # Build context
    context = PromptBuilder.build_function_context(func_symbol)

    assert context.name == "test_function"
    assert "param1: int" in context.signature
    assert "param2: str" in context.signature
    assert "-> bool" in context.signature
    assert "param1" in context.parameters
    assert "param2" in context.parameters
    assert context.return_type == "bool"
    assert not context.is_class_method


def test_prompt_building() -> None:
    """Test prompt building for different scenarios."""
    context = FunctionContext(
        name="test_func",
        signature="def test_func(x: int) -> str:",
        parameters=["x"],
        return_type="str",
        raises=set(),
        purpose="Test function",
    )

    # Test generation prompt
    prompt = PromptBuilder.build_generation_prompt(context)
    assert "Generate a Google-style docstring" in prompt
    assert "def test_func(x: int) -> str:" in prompt
    assert "Parameters: x" in prompt
    assert "Return type: str" in prompt

    # Test fix prompt
    fix_prompt = PromptBuilder.build_fix_prompt(
        context, "Old docstring", ["Missing parameter x"]
    )
    assert "Fix this Google-style docstring" in fix_prompt
    assert "Issues: Missing parameter x" in fix_prompt
    assert "Old docstring" in fix_prompt


def test_docstring_change_creation() -> None:
    """Test creating docstring change objects."""
    change = DocstringChange(
        symbol_name="test_func",
        symbol_kind="function",
        file_path="test.py",
        line_number=10,
        original_docstring="Old docstring",
        new_docstring="New docstring",
        change_type="modified",
        issues_addressed=["DG101", "DG202"],
    )

    assert change.symbol_name == "test_func"
    assert change.change_type == "modified"
    assert len(change.issues_addressed) == 2


def test_change_tracker() -> None:
    """Test change tracking functionality."""
    tracker = ChangeTracker()

    change1 = DocstringChange(
        symbol_name="func1",
        symbol_kind="function",
        file_path="test1.py",
        line_number=1,
        original_docstring="",
        new_docstring="New docstring",
        change_type="added",
        issues_addressed=["DG101"],
    )

    change2 = DocstringChange(
        symbol_name="func2",
        symbol_kind="function",
        file_path="test2.py",
        line_number=5,
        original_docstring="Old",
        new_docstring="New",
        change_type="modified",
        issues_addressed=["DG202"],
    )

    tracker.add_change(change1)
    tracker.add_change(change2)

    assert tracker.has_changes()
    assert len(tracker.changes) == 2
    assert len(tracker.get_changes_for_file("test1.py")) == 1
    assert len(tracker.get_changes_for_symbol("func1")) == 1

    summary = tracker.get_summary()
    assert "Total changes: 2" in summary
    assert "func1" in summary
    assert "func2" in summary


def test_diff_generation() -> None:
    """Test diff generation for docstring changes."""
    change = DocstringChange(
        symbol_name="test_func",
        symbol_kind="function",
        file_path="test.py",
        line_number=10,
        original_docstring="Old docstring",
        new_docstring="New docstring",
        change_type="modified",
        issues_addressed=["DG101"],
    )

    # Test unified diff
    unified_diff = DiffGenerator.generate_unified_diff(change)
    assert "--- test.py:10 (original)" in unified_diff
    assert "+++ test.py:10 (modified)" in unified_diff
    assert "Old docstring" in unified_diff
    assert "New docstring" in unified_diff

    # Test simple diff
    simple_diff = DiffGenerator.generate_simple_diff(change)
    assert "Original docstring:" in simple_diff
    assert "New docstring:" in simple_diff
    assert "Issues addressed: DG101" in simple_diff


@patch("dococtopy.remediation.llm.dspy")
def test_llm_config_creation(mock_dspy) -> None:
    """Test LLM configuration creation."""
    # Mock DSPy to avoid import errors
    mock_dspy.OpenAI = Mock()
    mock_dspy.Claude = Mock()
    mock_dspy.OllamaLocal = Mock()
    mock_dspy.settings = Mock()
    mock_dspy.Predict = Mock()

    config = LLMConfig(
        provider="openai",
        model="gpt-4o-mini",
        temperature=0.1,
        max_tokens=1000,
    )

    assert config.provider == "openai"
    assert config.model == "gpt-4o-mini"
    assert config.temperature == 0.1
    assert config.max_tokens == 1000


def test_remediation_options() -> None:
    """Test remediation options configuration."""
    options = RemediationOptions(
        dry_run=True,
        interactive=False,
        rule_ids={"DG101", "DG202"},
        max_changes=10,
    )

    assert options.dry_run is True
    assert options.interactive is False
    assert options.rule_ids == {"DG101", "DG202"}
    assert options.max_changes == 10


def test_remediation_engine_initialization() -> None:
    """Test remediation engine initialization."""
    from unittest.mock import patch

    options = RemediationOptions(dry_run=True)

    # Mock the LLM client creation to avoid API key requirement
    with patch("dococtopy.remediation.engine.create_llm_client") as mock_create_client:
        mock_client = mock_create_client.return_value

        # With DSPy installed, this should work
        engine = RemediationEngine(options)
        assert engine.options == options
        assert engine.llm_client == mock_client


def test_prompt_builder_edge_cases() -> None:
    """Test prompt builder with edge cases."""
    # Test with minimal context
    context = FunctionContext(
        name="minimal_func",
        signature="def minimal_func():",
        parameters=[],
        return_type=None,
        raises=set(),
        purpose="",
    )

    prompt = PromptBuilder.build_generation_prompt(context)
    assert "def minimal_func():" in prompt
    assert "Parameters:" not in prompt  # Should not include empty parameters
    assert "Return type:" not in prompt  # Should not include None return type

    # Test with existing docstring
    prompt_with_existing = PromptBuilder.build_generation_prompt(
        context, existing_docstring="Existing docstring"
    )
    assert "Existing docstring" in prompt_with_existing
    assert "Current docstring (to improve):" in prompt_with_existing
