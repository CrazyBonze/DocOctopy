# DocOctopy

A language-agnostic docstyle compliance & remediation tool that scans code for docstring/docblock presence and style, reports findings, and can auto-propose LLM-based fixes.

## Features

### 🔍 **Comprehensive Scanning**

- **Python-first** with extensible architecture for other languages
- **Google-style docstring validation** with detailed compliance checking
- **AST-based analysis** for accurate symbol and signature detection
- **Smart caching** with incremental scanning for large codebases

### 📊 **Multiple Output Formats**

- **Pretty console output** with Rich formatting
- **JSON reports** for CI/CD integration
- **SARIF format** for GitHub Code Scanning
- **Configurable exit codes** based on severity levels

### 🤖 **LLM-Powered Remediation**

- **Automatic docstring generation** for missing documentation
- **Smart fixing** of non-compliant docstrings
- **Enhancement** of existing docstrings with missing elements
- **DSPy integration** for reliable, structured LLM interactions

### ⚙️ **Flexible Configuration**

- **pyproject.toml integration** with rule enable/disable switches
- **Per-path overrides** for different project sections
- **Gitignore-style exclusions** with pathspec support
- **Rule severity customization** (error, warning, info, off)

## Installation

### Basic Installation

```bash
pip install dococtopy
```

### With LLM Support

```bash
pip install dococtopy[llm]
```

### Development Installation

```bash
git clone https://github.com/yourusername/dococtopy.git
cd dococtopy
pip install -e .
```

## Quick Start

### 1. Scan Your Code

```bash
# Scan current directory
dococtopy scan .

# Scan specific paths
dococtopy scan src/ tests/

# Get JSON output
dococtopy scan . --format json --output-file report.json

# Use SARIF for GitHub Code Scanning
dococtopy scan . --format sarif --output-file report.sarif
```

### 2. Fix Issues with LLM Assistance

```bash
# Dry-run mode (safe, shows what would be fixed)
dococtopy fix . --dry-run

# Fix specific rules only
dococtopy fix . --rule DG101,DG202 --dry-run

# Use different LLM provider
dococtopy fix . --llm-provider anthropic --llm-model claude-3-haiku-20240307
```

### 3. Configure Your Project

Create a `pyproject.toml` file:

```toml
[tool.docguard]
exclude = ["**/.venv/**", "**/build/**", "**/node_modules/**"]

[tool.docguard.rules]
DG101 = "error"    # Missing docstrings
DG201 = "error"    # Google style parse errors
DG202 = "error"    # Missing parameters
DG203 = "error"    # Extra parameters
DG204 = "warning"  # Returns section issues
DG205 = "info"     # Raises validation
DG301 = "warning"  # Summary style
DG302 = "warning"  # Blank line after summary
```

## Rules Reference

### Basic Compliance Rules

- **DG101**: Missing docstring (functions and classes)
- **DG301**: Summary first line should end with period
- **DG302**: Blank line required after summary

### Google Style Validation Rules

- **DG201**: Google style docstring parse error
- **DG202**: Parameter missing from docstring
- **DG203**: Extra parameter in docstring
- **DG204**: Returns section missing or mismatched
- **DG205**: Raises section validation

## Configuration

### pyproject.toml Settings

```toml
[tool.docguard]
# Paths to scan (default: current directory)
paths = ["src", "tests"]

# Exclude patterns (gitignore-style)
exclude = ["**/.venv/**", "**/build/**", "**/node_modules/**"]

# Rule configuration
[tool.docguard.rules]
DG101 = "error"      # error, warning, info, off
DG201 = "error"
DG202 = "warning"
DG203 = "warning"
DG204 = "info"
DG205 = "info"
DG301 = "warning"
DG302 = "warning"

# Per-path overrides
[[tool.docguard.overrides]]
patterns = ["tests/**"]
rules.DG101 = "off"  # Disable missing docstrings in tests
```

### Environment Variables

For LLM functionality:

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"

# Ollama (local)
# No API key needed, runs locally
```

## CLI Reference

### `dococtopy scan`

Scan paths for documentation compliance issues.

```bash
dococtopy scan [PATHS...] [OPTIONS]

Options:
  --format {pretty,json,sarif,both}  Output format [default: pretty]
  --config PATH                      Config file path [default: pyproject.toml]
  --fail-level {error,warning,info}  Exit code threshold [default: error]
  --no-cache                        Disable caching
  --changed-only                    Only scan changed files
  --stats                           Show cache statistics
  --output-file PATH                Write output to file
```

### `dococtopy fix`

Fix documentation issues using LLM assistance.

```bash
dococtopy fix [PATHS...] [OPTIONS]

Options:
  --dry-run                         Show changes without applying [default: True]
  --interactive                     Accept/reject each fix interactively
  --rule TEXT                       Comma-separated rule IDs to fix
  --max-changes INTEGER             Maximum number of changes
  --llm-provider {openai,anthropic,ollama}  LLM provider [default: openai]
  --llm-model TEXT                  LLM model to use [default: gpt-4o-mini]
  --config PATH                     Config file path
```

## Examples

### Example 1: Basic Project Scan

```bash
# Clone a project
git clone https://github.com/someuser/someproject.git
cd someproject

# Install DocOctopy
pip install dococtopy

# Scan for issues
dococtopy scan .

# Output:
# Scan Results
# Files scanned: 42
# Files compliant: 35
# Overall coverage: 83.3%
# 
#   src/main.py [NON_COMPLIANT] (Coverage: 60.0%)
#     [ERROR] DG101: Function 'process_data' is missing a docstring at 15:0
#     [WARNING] DG301: Docstring summary should end with a period. at 23:0
```

### Example 2: LLM-Powered Fixes

```bash
# Install with LLM support
pip install dococtopy[llm]

# Set up API key
export OPENAI_API_KEY="your-key"

# Fix issues (dry-run)
dococtopy fix . --dry-run

# Output:
# Scanning for documentation issues...
# Processing src/main.py...
# Found 2 changes for src/main.py
# 
# Change: process_data (function)
# Issues: DG101
# Dry run - no changes applied
# 
# Change: validate_input (function)
# Issues: DG202, DG301
# Dry run - no changes applied
# 
# Total changes: 2
# Run without --dry-run to apply changes
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/docstring-check.yml
name: Docstring Compliance
on: [push, pull_request]

jobs:
  docstring-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install dococtopy
      - run: dococtopy scan . --format json --output-file report.json --fail-level error
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: docstring-report
          path: report.json
```

## Architecture

DocOctopy is built with a modular, extensible architecture:

```bash
dococtopy/
├── cli/           # Command-line interface
├── core/          # Core engine, discovery, caching
├── adapters/      # Language-specific adapters
├── rules/         # Compliance rules and registry
├── remediation/   # LLM-powered fixing
└── reporters/     # Output formatters
```

### Key Components

- **Discovery Engine**: Finds files using gitignore-style patterns
- **Language Adapters**: Parse code and extract symbols/docstrings
- **Rule Engine**: Applies compliance rules with configurable severity
- **Remediation Engine**: Uses DSPy for structured LLM interactions
- **Caching System**: Incremental scanning with fingerprint-based invalidation

## Publishing

DocOctopy is automatically published to PyPI via GitHub Actions when a release is created.

### Manual Publishing (for maintainers)

1. **Update version** in `pyproject.toml`
2. **Build and test** the package:

   ```bash
   ./scripts/publish.sh
   ```

3. **Create a GitHub release** with tag `v0.1.0` (matching the version)
4. **GitHub Action** will automatically publish to PyPI

### PyPI Setup (one-time)

To enable automatic publishing, configure trusted publishing in PyPI:

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Navigate to "Publishing" → "Publishing tokens" → "Add a new pending publisher"
3. Configure:
   - **PyPI project name**: `dococtopy`
   - **Owner**: `yourusername` (your GitHub username)
   - **Repository name**: `dococtopy`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: (leave empty)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/dococtopy.git
cd dococtopy
uv sync --dev
uv run pytest
```

### Adding New Rules

1. Create rule class in `src/dococtopy/rules/`
2. Implement `check()` method
3. Register with `register()` function
4. Add tests in `tests/unit/`

### Adding New Languages

1. Implement `LanguageAdapter` interface
2. Create symbol extraction logic
3. Add language-specific rules
4. Update discovery patterns

## Roadmap

### MVP (Current)

- ✅ Python docstring compliance checking
- ✅ Google-style validation rules
- ✅ LLM-powered remediation
- ✅ Multiple output formats
- ✅ Configuration system
- ✅ Caching and incremental scanning

### V1 (Next)

- 🔄 Interactive fix workflows
- 🔄 File writing capabilities
- 🔄 GitHub Action and pre-commit hooks
- 🔄 Playground UI for prompt experimentation
- 🔄 Additional Python rules (coverage thresholds, etc.)

### Future

- 📋 JavaScript/TypeScript support
- 📋 Go documentation checking
- 📋 Rust documentation checking
- 📋 Language server integration
- 📋 Advanced prompt optimization

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [DSPy](https://github.com/stanfordnlp/dspy) for reliable LLM interactions
- Uses [docstring-parser](https://github.com/rr-/docstring_parser) for Google-style parsing
- Powered by [Typer](https://github.com/tiangolo/typer) for CLI interface
- Styled with [Rich](https://github.com/Textualize/rich) for beautiful output
# Test trigger
