from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from dococtopy.adapters.python.adapter import PythonSymbol
from dococtopy.core.findings import Finding, FindingLevel, Location
from dococtopy.rules.registry import register

try:
    from docstring_parser import parse
    from docstring_parser.common import DocstringStyle
except ImportError:
    parse = None  # type: ignore
    DocstringStyle = None  # type: ignore


@dataclass
class DG101MissingDocstring:
    id: str = "DG101"
    name: str = "Missing docstring"
    level_default: str = "error"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        for sym in symbols:
            if sym.kind in {"function", "class"} and not sym.docstring:
                findings.append(
                    Finding(  # type: ignore[call-arg]
                        rule_id=self.id,
                        level=FindingLevel.ERROR,
                        message=f"{sym.kind.capitalize()} '{sym.name}' is missing a docstring",
                        symbol=sym.name,
                        location=Location(line=sym.lineno, column=sym.col),
                    )
                )
        return findings


@dataclass
class DG301SummaryStyle:
    id: str = "DG301"
    name: str = "Summary first line should be a sentence with period"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        for sym in symbols:
            if sym.kind == "module":
                continue
            if sym.docstring:
                first_line = sym.docstring.strip().splitlines()[0].strip()
                if first_line and not first_line.endswith("."):
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Docstring summary should end with a period.",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
        return findings


@dataclass
class DG302BlankLineAfterSummary:
    id: str = "DG302"
    name: str = "Blank line required after summary"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        for sym in symbols:
            if sym.kind == "module" or not sym.docstring:
                continue
            lines = sym.docstring.splitlines()
            if len(lines) >= 2:
                # Google style: summary line, then blank line, then details/sections
                if lines[1].strip() != "":
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Expected blank line after docstring summary.",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
        return findings


@dataclass
class DG201GoogleStyleParseError:
    id: str = "DG201"
    name: str = "Google style docstring parse error"
    level_default: str = "error"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind == "module" or not sym.docstring:
                continue
            try:
                parse(sym.docstring, style=DocstringStyle.GOOGLE)
            except Exception as e:
                findings.append(
                    Finding(  # type: ignore[call-arg]
                        rule_id=self.id,
                        level=FindingLevel.ERROR,
                        message=f"Google style docstring parse error: {str(e)}",
                        symbol=sym.name,
                        location=Location(line=sym.lineno, column=sym.col),
                    )
                )
        return findings


@dataclass
class DG202ParamMissingFromDocstring:
    id: str = "DG202"
    name: str = "Parameter missing from docstring"
    level_default: str = "error"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Extract function parameters from AST
            func_params = self._extract_function_params(sym)
            if not func_params:
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                docstring_params = {param.arg_name for param in parsed.params}

                missing_params = func_params - docstring_params
                for param in missing_params:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.ERROR,
                            message=f"Parameter '{param}' missing from docstring",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _extract_function_params(self, sym: PythonSymbol) -> Set[str]:
        """Extract parameter names from function signature."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return set()

        params = set()
        for arg in sym.ast_node.args.args:
            if arg.arg != "self":  # Skip self parameter
                params.add(arg.arg)
        return params


@dataclass
class DG203ExtraParamInDocstring:
    id: str = "DG203"
    name: str = "Extra parameter in docstring"
    level_default: str = "error"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Extract function parameters from AST
            func_params = self._extract_function_params(sym)

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                docstring_params = {param.arg_name for param in parsed.params}

                extra_params = docstring_params - func_params
                for param in extra_params:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.ERROR,
                            message=f"Extra parameter '{param}' in docstring",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _extract_function_params(self, sym: PythonSymbol) -> Set[str]:
        """Extract parameter names from function signature."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return set()

        params = set()
        for arg in sym.ast_node.args.args:
            if arg.arg != "self":  # Skip self parameter
                params.add(arg.arg)
        return params


@dataclass
class DG204ReturnsSectionMissing:
    id: str = "DG204"
    name: str = "Returns section missing or mismatched"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Check if function has return annotation
            has_return_annotation = self._has_return_annotation(sym)

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                has_returns_section = parsed.returns is not None

                if has_return_annotation and not has_returns_section:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Function has return annotation but missing Returns section in docstring",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
                elif not has_return_annotation and has_returns_section:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Function has Returns section but no return annotation",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _has_return_annotation(self, sym: PythonSymbol) -> bool:
        """Check if function has return type annotation."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return False
        return sym.ast_node.returns is not None


@dataclass
class DG205RaisesSectionValidation:
    id: str = "DG205"
    name: str = "Raises section validation"
    level_default: str = "info"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Extract raised exceptions from AST
            raised_exceptions = self._extract_raised_exceptions(sym)

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                docstring_raises = {
                    raise_item.type_name for raise_item in parsed.raises
                }

                # Check for documented raises that aren't actually raised
                extra_raises = docstring_raises - raised_exceptions
                for exception in extra_raises:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.INFO,
                            message=f"Exception '{exception}' documented in Raises but not raised",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _extract_raised_exceptions(self, sym: PythonSymbol) -> Set[str]:
        """Extract exception types raised in function."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return set()

        exceptions = set()

        class RaiseVisitor(ast.NodeVisitor):
            def visit_Raise(self, node: ast.Raise) -> None:
                if node.exc and isinstance(node.exc, ast.Name):
                    exceptions.add(node.exc.id)
                elif (
                    node.exc
                    and isinstance(node.exc, ast.Call)
                    and isinstance(node.exc.func, ast.Name)
                ):
                    exceptions.add(node.exc.func.id)

        visitor = RaiseVisitor()
        visitor.visit(sym.ast_node)
        return exceptions


@dataclass
class DG206ArgsSectionFormat:
    """Check that Args section follows Google style format."""

    id: str = "DG206"
    name: str = "Args section should use proper Google style format"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if not sym.docstring:
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                if not parsed.params:
                    continue

                for param in parsed.params:
                    # Check if param description is missing
                    if not param.description or param.description.strip() == "":
                        findings.append(
                            Finding(  # type: ignore[call-arg]
                                rule_id=self.id,
                                level=FindingLevel.WARNING,
                                message=f"Parameter '{param.arg_name}' in Args section is missing description",
                                symbol=sym.name,
                                location=Location(line=sym.lineno, column=sym.col),
                            )
                        )
                    # Check if description starts with lowercase (should be capitalized)
                    elif param.description and param.description[0].islower():
                        findings.append(
                            Finding(  # type: ignore[call-arg]
                                rule_id=self.id,
                                level=FindingLevel.WARNING,
                                message=f"Parameter '{param.arg_name}' description should start with capital letter",
                                symbol=sym.name,
                                location=Location(line=sym.lineno, column=sym.col),
                            )
                        )
            except Exception:
                # Skip if parsing fails (handled by DG201)
                continue

        return findings


@dataclass
class DG207ReturnsSectionFormat:
    """Check that Returns section follows Google style format."""

    id: str = "DG207"
    name: str = "Returns section should use proper Google style format"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if not sym.docstring:
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                if not parsed.returns:
                    continue

                # Check if returns description is missing
                if (
                    not parsed.returns.description
                    or parsed.returns.description.strip() == ""
                ):
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Returns section is missing description",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
                # Check if description starts with lowercase (should be capitalized)
                elif (
                    parsed.returns.description
                    and parsed.returns.description[0].islower()
                ):
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Returns section description should start with capital letter",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if parsing fails (handled by DG201)
                continue

        return findings


@dataclass
class DG208RaisesSectionFormat:
    """Check that Raises section follows Google style format."""

    id: str = "DG208"
    name: str = "Raises section should use proper Google style format"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if not sym.docstring:
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                if not parsed.raises:
                    continue

                for raise_item in parsed.raises:
                    # Check if raises description is missing
                    if (
                        not raise_item.description
                        or raise_item.description.strip() == ""
                    ):
                        findings.append(
                            Finding(  # type: ignore[call-arg]
                                rule_id=self.id,
                                level=FindingLevel.WARNING,
                                message=f"Exception '{raise_item.type_name}' in Raises section is missing description",
                                symbol=sym.name,
                                location=Location(line=sym.lineno, column=sym.col),
                            )
                        )
                    # Check if description starts with lowercase (should be capitalized)
                    elif raise_item.description and raise_item.description[0].islower():
                        findings.append(
                            Finding(  # type: ignore[call-arg]
                                rule_id=self.id,
                                level=FindingLevel.WARNING,
                                message=f"Exception '{raise_item.type_name}' description should start with capital letter",
                                symbol=sym.name,
                                location=Location(line=sym.lineno, column=sym.col),
                            )
                        )
            except Exception:
                # Skip if parsing fails (handled by DG201)
                continue

        return findings


@dataclass
class DG209SummaryLength:
    """Check that summary is not too long or too short."""

    id: str = "DG209"
    name: str = "Summary should be appropriate length"
    level_default: str = "info"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if not sym.docstring:
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)
                if not parsed.short_description:
                    continue

                summary = parsed.short_description.strip()
                # Check if summary is too short (less than 10 characters)
                if len(summary) < 10:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.INFO,
                            message="Summary is too short (less than 10 characters)",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
                # Check if summary is too long (more than 80 characters)
                elif len(summary) > 80:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.INFO,
                            message="Summary is too long (more than 80 characters)",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if parsing fails (handled by DG201)
                continue

        return findings


@dataclass
class DG210DocstringIndentation:
    """Check that docstring indentation is consistent."""

    id: str = "DG210"
    name: str = "Docstring should have consistent indentation"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []

        for sym in symbols:
            if not sym.docstring:
                continue

            # Get the raw docstring lines
            docstring_lines = sym.docstring.split("\n")
            if len(docstring_lines) < 2:
                continue

            # Check if first line after opening quotes is indented
            first_content_line = None
            for i, line in enumerate(docstring_lines):
                if line.strip() and not line.strip().startswith('"""'):
                    first_content_line = i
                    break

            if first_content_line is None:
                continue

            # Check indentation consistency
            expected_indent = len(docstring_lines[first_content_line]) - len(
                docstring_lines[first_content_line].lstrip()
            )

            for i, line in enumerate(
                docstring_lines[first_content_line + 1 :], first_content_line + 1
            ):
                if line.strip() and not line.strip().startswith('"""'):
                    actual_indent = len(line) - len(line.lstrip())
                    if actual_indent != expected_indent:
                        findings.append(
                            Finding(  # type: ignore[call-arg]
                                rule_id=self.id,
                                level=FindingLevel.WARNING,
                                message=f"Inconsistent indentation in docstring (line {i + 1})",
                                symbol=sym.name,
                                location=Location(line=sym.lineno + i, column=sym.col),
                            )
                        )
                        break  # Only report first inconsistency

        return findings


@dataclass
class DG211YieldsSectionValidation:
    """Check that generator functions have proper Yields section."""

    id: str = "DG211"
    name: str = "Generator functions should have Yields section"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Check if function is a generator (has yield statements)
            if not self._is_generator_function(sym):
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)

                # Check if Yields section exists
                has_yields = any(
                    meta.args[0] == "yields"
                    for meta in parsed.meta
                    if meta.args and len(meta.args) > 0
                )

                if not has_yields:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Generator function should have Yields section",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _is_generator_function(self, sym: PythonSymbol) -> bool:
        """Check if function contains yield statements."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return False

        # Walk the entire AST tree to find yield statements
        for node in ast.walk(sym.ast_node):
            if isinstance(node, ast.Yield):
                return True
        return False


@dataclass
class DG212AttributesSectionValidation:
    """Check that classes with attributes document them properly."""

    id: str = "DG212"
    name: str = "Classes should document public attributes"
    level_default: str = "warning"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "class" or not sym.docstring:
                continue

            # Get public attributes from the class
            public_attrs = self._get_public_attributes(sym)
            if not public_attrs:
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)

                # Check if Attributes section exists in the raw docstring
                has_attributes = False
                if sym.docstring:
                    # Look for Attributes: or Attributes - patterns in the raw docstring
                    docstring_lower = sym.docstring.lower()
                    has_attributes = any(
                        pattern in docstring_lower
                        for pattern in [
                            "attributes:",
                            "attributes -",
                            "attributes\n",
                            "attributes ",
                        ]
                    )

                if not has_attributes:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.WARNING,
                            message="Class with public attributes should have Attributes section",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _get_public_attributes(self, sym: PythonSymbol) -> List[str]:
        """Get public attributes from class definition."""
        if not hasattr(sym, "ast_node") or not isinstance(sym.ast_node, ast.ClassDef):
            return []

        attrs = []
        # Look for assignments in the entire class AST tree
        for node in ast.walk(sym.ast_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        # Check if it's a self.attr assignment (public attribute)
                        if (
                            isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                        ):
                            if not target.attr.startswith("_"):
                                attrs.append(target.attr)
        return attrs


@dataclass
class DG213ExamplesSectionValidation:
    """Check that complex functions have Examples section."""

    id: str = "DG213"
    name: str = "Complex functions should have Examples section"
    level_default: str = "info"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Check if function is complex enough to warrant examples
            if not self._is_complex_function(sym):
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)

                # Check if Examples section exists
                if not parsed.examples:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.INFO,
                            message="Complex function should have Examples section",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _is_complex_function(self, sym: PythonSymbol) -> bool:
        """Check if function is complex enough to warrant examples."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return False

        # Consider complex if it has more than 3 parameters or more than 20 lines
        param_count = len(sym.ast_node.args.args)
        line_count = (
            sym.ast_node.end_lineno - sym.ast_node.lineno
            if sym.ast_node.end_lineno
            else 0
        )

        return param_count > 3 or line_count > 20


@dataclass
class DG214NoteSectionValidation:
    """Check that functions with special behavior have Note sections."""

    id: str = "DG214"
    name: str = "Functions with special behavior should have Note sections"
    level_default: str = "info"

    def check(self, *, symbols: List[PythonSymbol]) -> List[Finding]:
        findings: List[Finding] = []
        if parse is None or DocstringStyle is None:
            return findings

        for sym in symbols:
            if sym.kind != "function" or not sym.docstring:
                continue

            # Check if function has special behavior that should be noted
            if not self._has_special_behavior(sym):
                continue

            try:
                parsed = parse(sym.docstring, style=DocstringStyle.GOOGLE)

                # Check if Note section exists in the raw docstring
                has_note = False
                if sym.docstring:
                    # Look for Note: or Note - patterns in the raw docstring
                    docstring_lower = sym.docstring.lower()
                    has_note = any(
                        pattern in docstring_lower
                        for pattern in ["note:", "note -", "note\n", "note "]
                    )

                if not has_note:
                    findings.append(
                        Finding(  # type: ignore[call-arg]
                            rule_id=self.id,
                            level=FindingLevel.INFO,
                            message="Function with special behavior should have Note section",
                            symbol=sym.name,
                            location=Location(line=sym.lineno, column=sym.col),
                        )
                    )
            except Exception:
                # Skip if docstring parsing fails (handled by DG201)
                continue
        return findings

    def _has_special_behavior(self, sym: PythonSymbol) -> bool:
        """Check if function has special behavior that should be noted."""
        if not hasattr(sym, "ast_node") or not isinstance(
            sym.ast_node, ast.FunctionDef
        ):
            return False

        # Check for special patterns
        for node in ast.walk(sym.ast_node):
            # Check for *args or **kwargs
            if isinstance(node, ast.FunctionDef):
                if node.args.vararg or node.args.kwarg:
                    return True
            # Check for decorators
            if isinstance(node, ast.FunctionDef) and node.decorator_list:
                return True
            # Check for complex control flow
            if isinstance(node, (ast.For, ast.While, ast.If)) and len(node.body) > 5:
                return True

        return False


# Auto-register for MVP
register(DG101MissingDocstring())
register(DG301SummaryStyle())
register(DG302BlankLineAfterSummary())
register(DG201GoogleStyleParseError())
register(DG202ParamMissingFromDocstring())
register(DG203ExtraParamInDocstring())
register(DG204ReturnsSectionMissing())
register(DG205RaisesSectionValidation())
register(DG206ArgsSectionFormat())
register(DG207ReturnsSectionFormat())
register(DG208RaisesSectionFormat())
register(DG209SummaryLength())
register(DG210DocstringIndentation())
register(DG211YieldsSectionValidation())
register(DG212AttributesSectionValidation())
register(DG213ExamplesSectionValidation())
register(DG214NoteSectionValidation())
