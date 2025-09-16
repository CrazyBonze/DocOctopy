"""
Main CLI entry point for DocOctopy.
"""

from pathlib import Path
from typing import List, Optional, Set

import typer
from rich.console import Console
from rich.panel import Panel

from dococtopy import __version__
from dococtopy.core.config import load_config
from dococtopy.core.engine import scan_paths
from dococtopy.core.findings import FindingLevel
from dococtopy.remediation.engine import RemediationEngine, RemediationOptions
from dococtopy.remediation.llm import LLMConfig
from dococtopy.reporters.console import print_report
from dococtopy.reporters.json_reporter import to_json
from dococtopy.reporters.sarif import to_sarif

# Create the main app
app = typer.Typer(
    name="dococtopy",
    help="A language-agnostic docstyle compliance & remediation tool.",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"dococtopy {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version and exit."
    )
):
    """DocOctopy - Docstring compliance and remediation tool."""
    pass


@app.command()
def scan(
    paths: List[Path] = typer.Argument(
        ...,
        help="Paths to scan for documentation issues.",
        exists=True,
    ),
    format: str = typer.Option(
        "pretty", "--format", "-f", help="Output format: pretty, json, sarif, both"
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", help="Path to config file (default: pyproject.toml)"
    ),
    fail_level: str = typer.Option(
        "error",
        "--fail-level",
        help="Exit with error if findings at this level or above: error, warning, info",
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Disable on-disk cache for scanning"
    ),
    changed_only: bool = typer.Option(
        False, "--changed-only", help="Only process files whose fingerprint changed"
    ),
    stats: bool = typer.Option(
        False, "--stats", help="Show cache performance statistics"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output-file", "-o", help="Write JSON report to file"
    ),
):
    """Scan paths for documentation compliance issues."""
    cfg = load_config(config)
    report, scan_stats = scan_paths(
        paths, config=cfg, use_cache=not no_cache, changed_only=changed_only
    )

    if format in ("pretty", "both"):
        import sys

        print_report(report, sys.stdout, stats=scan_stats if stats else None)
    if format in ("json", "both"):
        # Use plain stdout to ensure clean JSON without Rich formatting
        import sys

        json_output = to_json(report)
        if output_file:
            output_file.write_text(json_output, encoding="utf-8")
        else:
            sys.stdout.write(json_output + "\n")
    if format == "sarif":
        import json
        import sys

        sarif_output = json.dumps(to_sarif(report), indent=2)
        if output_file:
            output_file.write_text(sarif_output, encoding="utf-8")
        else:
            sys.stdout.write(sarif_output + "\n")

    target_level = fail_level.lower()
    level_order = {"info": 0, "warning": 1, "error": 2}
    threshold = level_order.get(target_level, 2)

    def level_to_ord(lv: FindingLevel) -> int:
        return level_order.get(str(lv.value if hasattr(lv, "value") else lv), 2)

    has_failure = any(
        level_to_ord(f.level) >= threshold for fr in report.files for f in fr.findings
    )
    raise typer.Exit(code=1 if has_failure else 0)


@app.command()
def fix(
    paths: List[Path] = typer.Argument(
        ..., help="Paths to fix documentation issues in.", exists=True
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run", help="Show what would be fixed without making changes."
    ),
    interactive: bool = typer.Option(
        False, "--interactive", help="Interactively accept/reject each fix."
    ),
    rule: Optional[str] = typer.Option(
        None,
        "--rule",
        help="Comma-separated list of rule IDs to fix (e.g., DG101,DG202).",
    ),
    max_changes: Optional[int] = typer.Option(
        None, "--max-changes", help="Maximum number of changes to make."
    ),
    llm_provider: str = typer.Option(
        "openai", "--llm-provider", help="LLM provider: openai, anthropic, ollama."
    ),
    llm_model: str = typer.Option(
        "gpt-4o-mini", "--llm-model", help="LLM model to use."
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", help="Path to config file (default: pyproject.toml)"
    ),
):
    """Fix documentation issues using LLM assistance."""
    try:
        # Parse rule IDs
        rule_ids = None
        if rule:
            rule_ids = set(rule.split(","))

        # Create LLM config
        llm_config = LLMConfig(
            provider=llm_provider,
            model=llm_model,
        )

        # Create remediation options
        options = RemediationOptions(
            dry_run=dry_run,
            interactive=interactive,
            rule_ids=rule_ids,
            max_changes=max_changes,
            llm_config=llm_config,
        )

        # Create remediation engine
        engine = RemediationEngine(options)

        # Load configuration
        cfg = load_config(config)

        # Scan for issues
        console.print("[blue]Scanning for documentation issues...[/blue]")
        report, _ = scan_paths(paths, config=cfg, use_cache=True)

        if not report.files:
            console.print("[green]No files found to process.[/green]")
            return

        # Process each file
        total_changes = 0
        for file_result in report.files:
            if not file_result.findings:
                continue

            console.print(f"[blue]Processing {file_result.path}...[/blue]")

            # Load symbols for this file
            from dococtopy.adapters.python.adapter import load_symbols_from_file

            symbols = load_symbols_from_file(file_result.path)

            # Remediate the file
            changes = engine.remediate_file(
                file_result.path,
                symbols,
                file_result.findings,
            )

            if changes:
                total_changes += len(changes)
                console.print(
                    f"[green]Found {len(changes)} changes for {file_result.path}[/green]"
                )

                # Show changes
                for change in changes:
                    console.print(
                        f"\n[cyan]Change: {change.symbol_name} ({change.symbol_kind})[/cyan]"
                    )
                    console.print(
                        f"[yellow]Issues: {', '.join(change.issues_addressed)}[/yellow]"
                    )

                    if dry_run:
                        console.print("[dim]Dry run - no changes applied[/dim]")
                    else:
                        console.print("[green]Applied fix[/green]")

        # Show summary
        if total_changes > 0:
            console.print(f"\n[green]Total changes: {total_changes}[/green]")
            if dry_run:
                console.print("[yellow]Run without --dry-run to apply changes[/yellow]")
        else:
            console.print("[green]No changes needed![/green]")

    except ImportError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            "[yellow]Install LLM dependencies with: pip install dococtopy[llm][/yellow]"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error during remediation: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config_init():
    """Initialize a default configuration file."""
    console.print("[yellow]Config init not yet implemented.[/yellow]")
    console.print("This will create a default pyproject.toml configuration.")


if __name__ == "__main__":
    app()
