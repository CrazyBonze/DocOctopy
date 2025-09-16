"""Prompt builder for Google-style docstring generation.

This module provides utilities for building context-rich prompts
that help LLMs generate high-quality Google-style docstrings.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List, Optional, Set

from dococtopy.adapters.python.adapter import PythonSymbol


@dataclass
class FunctionContext:
    """Context information about a function for docstring generation."""

    name: str
    signature: str
    parameters: List[str]
    return_type: Optional[str]
    raises: Set[str]
    purpose: str
    is_class_method: bool = False
    is_async: bool = False


class PromptBuilder:
    """Builder for creating context-rich prompts for docstring generation."""

    @staticmethod
    def build_function_context(symbol: PythonSymbol) -> FunctionContext:
        """Extract context information from a Python symbol."""
        if not hasattr(symbol, "ast_node") or not isinstance(
            symbol.ast_node, ast.FunctionDef
        ):
            # Fallback for symbols without AST nodes
            return FunctionContext(
                name=symbol.name,
                signature=symbol.name,
                parameters=[],
                return_type=None,
                raises=set(),
                purpose="",
            )

        node = symbol.ast_node

        # Extract parameters
        parameters = []
        for arg in node.args.args:
            if arg.arg != "self":  # Skip self parameter
                parameters.append(arg.arg)

        # Extract return type
        return_type = None
        if node.returns:
            return_type = (
                ast.unparse(node.returns)
                if hasattr(ast, "unparse")
                else str(node.returns)
            )

        # Extract raised exceptions
        raises = set()

        class RaiseVisitor(ast.NodeVisitor):
            def visit_Raise(self, node: ast.Raise) -> None:
                if node.exc and isinstance(node.exc, ast.Name):
                    raises.add(node.exc.id)
                elif (
                    node.exc
                    and isinstance(node.exc, ast.Call)
                    and isinstance(node.exc.func, ast.Name)
                ):
                    raises.add(node.exc.func.id)

        visitor = RaiseVisitor()
        visitor.visit(node)

        # Build signature string
        signature_parts = []
        if isinstance(node, ast.AsyncFunctionDef):
            signature_parts.append("async")
        signature_parts.append("def")
        signature_parts.append(node.name)

        # Add parameters
        param_parts = []
        for arg in node.args.args:
            param_str = arg.arg
            if arg.annotation:
                annotation_str = (
                    ast.unparse(arg.annotation)
                    if hasattr(ast, "unparse")
                    else str(arg.annotation)
                )
                param_str += f": {annotation_str}"
            param_parts.append(param_str)

        if param_parts:
            signature_parts.append(f"({', '.join(param_parts)})")
        else:
            signature_parts.append("()")

        # Add return type
        if node.returns:
            return_type_str = (
                ast.unparse(node.returns)
                if hasattr(ast, "unparse")
                else str(node.returns)
            )
            signature_parts.append(f" -> {return_type_str}")

        signature = " ".join(signature_parts)

        # Determine if it's a class method
        is_class_method = False
        if node.args.args and node.args.args[0].arg == "self":
            is_class_method = True

        return FunctionContext(
            name=symbol.name,
            signature=signature,
            parameters=parameters,
            return_type=return_type,
            raises=raises,
            purpose="",  # Will be filled by user or inferred
            is_class_method=is_class_method,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    @staticmethod
    def build_generation_prompt(
        context: FunctionContext, existing_docstring: str = ""
    ) -> str:
        """Build a prompt for generating a new docstring."""
        prompt_parts = [
            f"Generate a Google-style docstring for this Python function:",
            f"",
            f"```python",
            f"{context.signature}",
            f"    pass",
            f"```",
            f"",
        ]

        if context.purpose:
            prompt_parts.extend(
                [
                    f"Purpose: {context.purpose}",
                    f"",
                ]
            )

        if context.parameters:
            prompt_parts.extend(
                [
                    f"Parameters: {', '.join(context.parameters)}",
                    f"",
                ]
            )

        if context.return_type:
            prompt_parts.extend(
                [
                    f"Return type: {context.return_type}",
                    f"",
                ]
            )

        if context.raises:
            prompt_parts.extend(
                [
                    f"May raise: {', '.join(sorted(context.raises))}",
                    f"",
                ]
            )

        if existing_docstring:
            prompt_parts.extend(
                [
                    f"Current docstring (to improve):",
                    f'"""',
                    existing_docstring,
                    f'"""',
                    f"",
                ]
            )

        prompt_parts.extend(
            [
                f"Requirements:",
                f"- Start with a one-line summary ending with a period",
                f"- Add a blank line after the summary",
                f"- Include Args section for each parameter (except self)",
                f"- Include Returns section if function has return type",
                f"- Include Raises section for documented exceptions",
                f"- Use Google style format",
                f"",
                f"Generated docstring:",
            ]
        )

        return "\n".join(prompt_parts)

    @staticmethod
    def build_fix_prompt(
        context: FunctionContext, current_docstring: str, issues: List[str]
    ) -> str:
        """Build a prompt for fixing a non-compliant docstring."""
        prompt_parts = [
            f"Fix this Google-style docstring to address the following issues:",
            f"",
            f"Issues: {', '.join(issues)}",
            f"",
            f"Function signature:",
            f"```python",
            f"{context.signature}",
            f"    pass",
            f"```",
            f"",
            f"Current docstring:",
            f'"""',
            current_docstring,
            f'"""',
            f"",
            f"Requirements:",
            f"- Fix all identified issues",
            f"- Maintain Google style format",
            f"- Include all parameters in Args section",
            f"- Include Returns section if function has return type",
            f"- Include Raises section for documented exceptions",
            f"",
            f"Fixed docstring:",
        ]

        return "\n".join(prompt_parts)

    @staticmethod
    def build_enhancement_prompt(
        context: FunctionContext, current_docstring: str, missing_elements: List[str]
    ) -> str:
        """Build a prompt for enhancing an existing docstring."""
        prompt_parts = [
            f"Enhance this Google-style docstring by adding the missing elements:",
            f"",
            f"Missing elements: {', '.join(missing_elements)}",
            f"",
            f"Function signature:",
            f"```python",
            f"{context.signature}",
            f"    pass",
            f"```",
            f"",
            f"Current docstring:",
            f'"""',
            current_docstring,
            f'"""',
            f"",
            f"Requirements:",
            f"- Add all missing elements",
            f"- Maintain existing content where appropriate",
            f"- Follow Google style format",
            f"- Ensure all parameters are documented",
            f"",
            f"Enhanced docstring:",
        ]

        return "\n".join(prompt_parts)
