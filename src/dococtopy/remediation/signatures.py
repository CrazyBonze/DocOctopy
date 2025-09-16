"""DSPy signatures for docstring generation and remediation.

This module defines the input/output contracts for LLM-based docstring generation
using DSPy's declarative approach.
"""

from __future__ import annotations

try:
    import dspy
except ImportError:
    dspy = None  # type: ignore


class DocstringGeneration(dspy.Signature if dspy else object):  # type: ignore
    """Generate a Google-style docstring for a Python function or class.

    This signature defines the contract for generating compliant docstrings
    based on function/class signatures and context.
    """

    function_signature: str = dspy.InputField(  # type: ignore
        desc="The Python function or class signature including parameters and return type"
    )
    function_purpose: str = dspy.InputField(  # type: ignore
        desc="Brief description of what the function/class does"
    )
    existing_docstring: str = dspy.InputField(  # type: ignore
        desc="Current docstring (if any) to improve or replace"
    )
    context: str = dspy.InputField(  # type: ignore
        desc="Additional context about the function's usage, parameters, or behavior"
    )

    docstring: str = dspy.OutputField(  # type: ignore
        desc="Generated Google-style docstring following the format: summary, blank line, Args section (if applicable), Returns section (if applicable), Raises section (if applicable)"
    )


class DocstringFix(dspy.Signature if dspy else object):  # type: ignore
    """Fix a non-compliant docstring to meet Google style standards.

    This signature is used when we have an existing docstring that needs
    to be corrected rather than generated from scratch.
    """

    function_signature: str = dspy.InputField(  # type: ignore
        desc="The Python function or class signature"
    )
    current_docstring: str = dspy.InputField(  # type: ignore
        desc="The current non-compliant docstring"
    )
    issues: str = dspy.InputField(  # type: ignore
        desc="Description of the specific compliance issues found"
    )

    fixed_docstring: str = dspy.OutputField(  # type: ignore
        desc="Corrected Google-style docstring that addresses all compliance issues"
    )


class DocstringEnhancement(dspy.Signature if dspy else object):  # type: ignore
    """Enhance an existing docstring with missing information.

    This signature is used to add missing parameters, return descriptions,
    or other sections to an existing docstring.
    """

    function_signature: str = dspy.InputField(  # type: ignore
        desc="The Python function or class signature"
    )
    current_docstring: str = dspy.InputField(  # type: ignore
        desc="The current docstring that needs enhancement"
    )
    missing_elements: str = dspy.InputField(  # type: ignore
        desc="Description of what's missing (e.g., 'missing parameter xyz', 'missing Returns section')"
    )

    enhanced_docstring: str = dspy.OutputField(  # type: ignore
        desc="Enhanced docstring with all missing elements added in Google style"
    )


# Export signatures for use in other modules
__all__ = [
    "DocstringGeneration",
    "DocstringFix",
    "DocstringEnhancement",
]
