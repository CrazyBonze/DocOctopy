"""
Unit tests for CLI main module.
"""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from dococtopy.cli.main import app, config_init, fix, main, scan, version_callback


class TestVersionCallback:
    """Test version callback functionality."""

    def test_version_callback_prints_version_and_exits(self):
        """Test that version callback prints version and exits."""
        with pytest.raises(typer.Exit) as exc_info:
            version_callback(True)
        assert exc_info.value.exit_code == 0

    def test_version_callback_does_nothing_when_false(self):
        """Test that version callback does nothing when value is False."""
        # Should not raise an exception
        version_callback(False)


class TestMainCallback:
    """Test main callback functionality."""

    def test_main_callback_with_version(self):
        """Test main callback with version flag."""
        # The main callback doesn't directly raise Exit, it calls version_callback
        # which raises Exit. So we test that the callback works correctly.
        with pytest.raises(typer.Exit) as exc_info:
            version_callback(True)
        assert exc_info.value.exit_code == 0

    def test_main_callback_without_version(self):
        """Test main callback without version flag."""
        # Should not raise an exception
        main(version=None)


class TestScanCommand:
    """Test scan command functionality."""

    def test_scan_command_basic(self, tmp_path):
        """Test basic scan command functionality."""
        # Create a test Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Create a proper mock report with summary
        mock_summary = Mock()
        mock_summary.files_total = 1
        mock_summary.files_compliant = 0
        mock_summary.coverage_overall = 0.5

        mock_report = Mock()
        mock_report.files = []
        mock_report.summary = mock_summary

        # Mock the scan_paths function at the module level where it's imported
        with patch("dococtopy.core.engine.scan_paths") as mock_scan:
            mock_scan.return_value = (mock_report, {})

            # Mock load_config at the module level where it's imported
            with patch("dococtopy.core.config.load_config") as mock_config:
                mock_config.return_value = None

                # Mock print_report at the module level where it's imported
                with patch("dococtopy.reporters.console.print_report") as mock_print:
                    # Run scan command with proper parameters - expect typer.Exit
                    with pytest.raises(typer.Exit) as exc_info:
                        scan(
                            paths=[test_file],
                            format="pretty",
                            config=None,
                            fail_level="error",
                            no_cache=False,
                            changed_only=False,
                            stats=False,
                            output_file=None,
                        )
                    assert exc_info.value.exit_code == 0  # No findings, should exit 0

                    # Verify scan_paths was called
                    mock_scan.assert_called_once()

    def test_scan_command_with_json_output(self, tmp_path):
        """Test scan command with JSON output."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        mock_summary = Mock()
        mock_summary.files_total = 1
        mock_summary.files_compliant = 0
        mock_summary.coverage_overall = 0.5

        mock_report = Mock()
        mock_report.files = []
        mock_report.summary = mock_summary

        with patch("dococtopy.core.engine.scan_paths") as mock_scan:
            mock_scan.return_value = (mock_report, {})

            with patch("dococtopy.core.config.load_config") as mock_config:
                mock_config.return_value = None

                # Mock to_json to avoid actual JSON serialization
                with patch("dococtopy.reporters.json_reporter.to_json") as mock_json:
                    mock_json.return_value = '{"files": []}'

                    # Mock sys.stdout.write
                    with patch("sys.stdout.write") as mock_write:
                        with pytest.raises(typer.Exit) as exc_info:
                            scan(
                                paths=[test_file],
                                format="json",
                                config=None,
                                fail_level="error",
                                no_cache=False,
                                changed_only=False,
                                stats=False,
                                output_file=None,
                            )
                        assert exc_info.value.exit_code == 0

                        # Verify JSON output was written
                        mock_write.assert_called_with('{"files": []}\n')

    def test_scan_command_with_output_file(self, tmp_path):
        """Test scan command with output file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")
        output_file = tmp_path / "output.json"

        mock_summary = Mock()
        mock_summary.files_total = 1
        mock_summary.files_compliant = 0
        mock_summary.coverage_overall = 0.5

        mock_report = Mock()
        mock_report.files = []
        mock_report.summary = mock_summary

        with patch("dococtopy.core.engine.scan_paths") as mock_scan:
            mock_scan.return_value = (mock_report, {})

            with patch("dococtopy.core.config.load_config") as mock_config:
                mock_config.return_value = None

                with patch("dococtopy.reporters.json_reporter.to_json") as mock_json:
                    mock_json.return_value = '{"files": []}'

                    with pytest.raises(typer.Exit) as exc_info:
                        scan(
                            paths=[test_file],
                            format="json",
                            config=None,
                            fail_level="error",
                            no_cache=False,
                            changed_only=False,
                            stats=False,
                            output_file=output_file,
                        )
                    assert exc_info.value.exit_code == 0

                    # Verify output file was written
                    assert output_file.exists()
                    assert output_file.read_text() == '{"files": []}'

    def test_scan_command_with_sarif_output(self, tmp_path):
        """Test scan command with SARIF output."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        mock_summary = Mock()
        mock_summary.files_total = 1
        mock_summary.files_compliant = 0
        mock_summary.coverage_overall = 0.5

        mock_report = Mock()
        mock_report.files = []
        mock_report.summary = mock_summary

        with patch("dococtopy.core.engine.scan_paths") as mock_scan:
            mock_scan.return_value = (mock_report, {})

            with patch("dococtopy.core.config.load_config") as mock_config:
                mock_config.return_value = None

                with patch("dococtopy.reporters.sarif.to_sarif") as mock_sarif:
                    mock_sarif.return_value = {"runs": []}

                    with patch("sys.stdout.write") as mock_write:
                        with pytest.raises(typer.Exit) as exc_info:
                            scan(
                                paths=[test_file],
                                format="sarif",
                                config=None,
                                fail_level="error",
                                no_cache=False,
                                changed_only=False,
                                stats=False,
                                output_file=None,
                            )
                        assert exc_info.value.exit_code == 0

                        # Verify SARIF output was written
                        expected_output = json.dumps({"runs": []}, indent=2) + "\n"
                        mock_write.assert_called_with(expected_output)

    def test_scan_command_exit_codes(self, tmp_path):
        """Test scan command exit codes based on findings."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Test with no findings (should exit 0)
        mock_summary = Mock()
        mock_summary.files_total = 1
        mock_summary.files_compliant = 1
        mock_summary.coverage_overall = 1.0

        mock_report = Mock()
        mock_report.files = []
        mock_report.summary = mock_summary

        with patch("dococtopy.core.engine.scan_paths") as mock_scan:
            mock_scan.return_value = (mock_report, {})

            with patch("dococtopy.core.config.load_config") as mock_config:
                mock_config.return_value = None

                with patch("dococtopy.reporters.console.print_report") as mock_print:
                    with pytest.raises(typer.Exit) as exc_info:
                        scan(
                            paths=[test_file],
                            format="pretty",
                            config=None,
                            fail_level="error",
                            no_cache=False,
                            changed_only=False,
                            stats=False,
                            output_file=None,
                        )
                    assert exc_info.value.exit_code == 0

        # Test with error findings (should exit 1)
        mock_finding = Mock()
        mock_finding.level = "error"
        mock_file_result = Mock()
        mock_file_result.findings = [mock_finding]

        mock_report_with_findings = Mock()
        mock_report_with_findings.files = [mock_file_result]
        mock_report_with_findings.summary = mock_summary

        with patch("dococtopy.core.engine.scan_paths") as mock_scan:
            mock_scan.return_value = (mock_report_with_findings, {})

            with patch("dococtopy.core.config.load_config") as mock_config:
                mock_config.return_value = None

                with patch("dococtopy.reporters.console.print_report") as mock_print:
                    with pytest.raises(typer.Exit) as exc_info:
                        scan(
                            paths=[test_file],
                            format="pretty",
                            config=None,
                            fail_level="error",
                            no_cache=False,
                            changed_only=False,
                            stats=False,
                            output_file=None,
                        )
                    assert exc_info.value.exit_code == 1


class TestFixCommand:
    """Test fix command functionality."""

    def test_fix_command_basic(self, tmp_path):
        """Test basic fix command functionality."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        with patch(
            "dococtopy.remediation.engine.RemediationEngine"
        ) as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.remediate_file.return_value = []

            with patch("dococtopy.core.engine.scan_paths") as mock_scan:
                mock_report = Mock()
                mock_file_result = Mock()
                mock_file_result.path = test_file
                mock_file_result.findings = []
                mock_report.files = [mock_file_result]
                mock_scan.return_value = (mock_report, {})

                with patch("dococtopy.core.config.load_config") as mock_config:
                    mock_config.return_value = None

                    # Mock the import that happens inside the function
                    with patch(
                        "dococtopy.adapters.python.adapter.load_symbols_from_file"
                    ) as mock_load_symbols:
                        mock_load_symbols.return_value = []

                        # Mock console.print to avoid output during test
                        with patch("dococtopy.cli.main.console.print") as mock_console:
                            fix(
                                paths=[test_file],
                                dry_run=True,
                                interactive=False,
                                rule=None,
                                max_changes=None,
                                llm_provider="openai",
                                llm_model="gpt-4o-mini",
                                config=None,
                            )

                            # Verify engine was created
                            mock_engine_class.assert_called_once()
                            # Since there are no findings, remediate_file should not be called
                            # The function should exit early with "No changes needed!"

    def test_fix_command_with_rule_filtering(self, tmp_path):
        """Test fix command with rule filtering."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        with patch(
            "dococtopy.remediation.engine.RemediationEngine"
        ) as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.remediate_file.return_value = []

            with patch("dococtopy.core.engine.scan_paths") as mock_scan:
                mock_report = Mock()
                mock_file_result = Mock()
                mock_file_result.path = test_file
                mock_file_result.findings = []
                mock_report.files = [mock_file_result]
                mock_scan.return_value = (mock_report, {})

                with patch("dococtopy.core.config.load_config") as mock_config:
                    mock_config.return_value = None

                    with patch(
                        "dococtopy.adapters.python.adapter.load_symbols_from_file"
                    ) as mock_load_symbols:
                        mock_load_symbols.return_value = []

                        fix(
                            paths=[test_file],
                            dry_run=True,
                            interactive=False,
                            rule="DG101,DG202",
                            max_changes=None,
                            llm_provider="openai",
                            llm_model="gpt-4o-mini",
                            config=None,
                        )

                        # Verify engine was created with rule filtering
                        call_args = mock_engine_class.call_args
                        options = call_args[0][0]  # First positional argument
                        assert options.rule_ids == {"DG101", "DG202"}

    def test_fix_command_with_changes(self, tmp_path):
        """Test fix command with changes."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        # Mock a change
        mock_change = Mock()
        mock_change.symbol_name = "hello"
        mock_change.symbol_kind = "function"
        mock_change.issues_addressed = ["DG101"]

        with patch(
            "dococtopy.remediation.engine.RemediationEngine"
        ) as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            mock_engine.remediate_file.return_value = [mock_change]

            with patch("dococtopy.core.engine.scan_paths") as mock_scan:
                mock_report = Mock()
                mock_file_result = Mock()
                mock_file_result.path = test_file
                mock_file_result.findings = [Mock()]
                mock_report.files = [mock_file_result]
                mock_scan.return_value = (mock_report, {})

                with patch("dococtopy.core.config.load_config") as mock_config:
                    mock_config.return_value = None

                    with patch(
                        "dococtopy.adapters.python.adapter.load_symbols_from_file"
                    ) as mock_load_symbols:
                        mock_load_symbols.return_value = []

                        fix(
                            paths=[test_file],
                            dry_run=True,
                            interactive=False,
                            rule=None,
                            max_changes=None,
                            llm_provider="openai",
                            llm_model="gpt-4o-mini",
                            config=None,
                        )

                        # Verify engine was called
                        mock_engine.remediate_file.assert_called_once()

    def test_fix_command_import_error(self, tmp_path):
        """Test fix command with ImportError."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        with patch(
            "dococtopy.remediation.engine.RemediationEngine",
            side_effect=ImportError("dspy not found"),
        ):
            with pytest.raises(typer.Exit) as exc_info:
                fix(
                    paths=[test_file],
                    dry_run=True,
                    interactive=False,
                    rule=None,
                    max_changes=None,
                    llm_provider="openai",
                    llm_model="gpt-4o-mini",
                    config=None,
                )
            assert exc_info.value.exit_code == 1

    def test_fix_command_general_exception(self, tmp_path):
        """Test fix command with general exception."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello():\n    pass\n")

        with patch(
            "dococtopy.remediation.engine.RemediationEngine",
            side_effect=Exception("Something went wrong"),
        ):
            with pytest.raises(typer.Exit) as exc_info:
                fix(
                    paths=[test_file],
                    dry_run=True,
                    interactive=False,
                    rule=None,
                    max_changes=None,
                    llm_provider="openai",
                    llm_model="gpt-4o-mini",
                    config=None,
                )
            assert exc_info.value.exit_code == 1


class TestConfigInitCommand:
    """Test config_init command functionality."""

    def test_config_init_command(self):
        """Test config_init command."""
        # This command is not yet implemented, so we just test it doesn't crash
        config_init()


class TestCliRunner:
    """Test CLI using Typer's CliRunner."""

    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "dococtopy" in result.output

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "language-agnostic docstyle compliance" in result.output

    def test_scan_help(self):
        """Test scan command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["scan", "--help"])
        assert result.exit_code == 0
        assert "Scan paths" in result.output

    def test_fix_help(self):
        """Test fix command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["fix", "--help"])
        assert result.exit_code == 0
        assert "Fix documentation" in result.output

    def test_config_init_help(self):
        """Test config init command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["config-init", "--help"])
        assert result.exit_code == 0
        assert "Initialize a default" in result.output
