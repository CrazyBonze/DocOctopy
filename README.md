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
- **Interactive review mode** with diff preview and approval workflow
- **Multiple LLM providers** (OpenAI, Anthropic, Ollama)

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
git clone https://github.com/CrazyBonze/DocOctopy.git
cd DocOctopy
uv sync --group dev
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

# Interactive mode (review each change)
dococtopy fix . --interactive

# Fix specific rules only
dococtopy fix . --rule DG101,DG202 --dry-run

# Use different LLM provider
dococtopy fix . --llm-provider anthropic --llm-model claude-3-haiku-20240307

# Use local Ollama server
dococtopy fix . --llm-provider ollama --llm-model codeqwen:latest --llm-base-url http://localhost:11434
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
DG211 = "info"     # Yields section validation
DG212 = "info"     # Attributes section validation
DG213 = "info"     # Examples section validation
DG214 = "info"     # Note section validation
```

## How to Get Started

### Step 1: Install DocOctopy

```bash
# Install with LLM support for automatic fixes
pip install dococtopy[llm]
```

### Step 2: Set Up LLM Provider

Choose one of these options:

#### Option A: Local Ollama (Recommended for Development)

1. **Install Ollama**: [Download from ollama.ai](https://ollama.ai)
2. **Pull a model**:

   ```bash
   ollama pull codeqwen:latest
   # or
   ollama pull llama3.1:8b
   ```

3. **Test DocOctopy**:

   ```bash
   dococtopy fix . --llm-provider ollama --llm-model codeqwen:latest --llm-base-url http://localhost:11434 --dry-run
   ```

#### Option B: OpenAI

1. **Get API key**: [OpenAI API Keys](https://platform.openai.com/api-keys)
2. **Set environment variable**:

   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

3. **Test DocOctopy**:

   ```bash
   dococtopy fix . --llm-provider openai --llm-model gpt-4o-mini --dry-run
   ```

#### Option C: Anthropic

1. **Get API key**: [Anthropic Console](https://console.anthropic.com/)
2. **Set environment variable**:

   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

3. **Test DocOctopy**:

   ```bash
   dococtopy fix . --llm-provider anthropic --llm-model claude-3-haiku-20240307 --dry-run
   ```

### Step 3: Scan Your Project

```bash
# Basic scan
dococtopy scan .

# Get detailed report
dococtopy scan . --format json --output-file docstring-report.json
```

### Step 4: Fix Issues

```bash
# See what would be fixed (safe)
dococtopy fix . --dry-run

# Interactive mode (review each change)
dococtopy fix . --interactive

# Apply fixes automatically
dococtopy fix . --llm-provider ollama --llm-model codeqwen:latest
```

### Step 5: Configure Your Project

Create `pyproject.toml`:

```toml
[tool.docguard]
# Exclude common directories
exclude = ["**/.venv/**", "**/build/**", "**/node_modules/**", "**/tests/**"]

# Configure rule severity
[tool.docguard.rules]
DG101 = "error"      # Missing docstrings
DG201 = "error"      # Google style parse errors
DG202 = "warning"    # Missing parameters
DG203 = "warning"    # Extra parameters
DG204 = "info"       # Returns section issues
DG205 = "info"       # Raises validation
DG301 = "warning"    # Summary style
DG302 = "warning"    # Blank line after summary
DG211 = "info"       # Yields section validation
DG212 = "info"       # Attributes section validation
DG213 = "info"       # Examples section validation
DG214 = "info"       # Note section validation

# Per-path overrides
[[tool.docguard.overrides]]
patterns = ["tests/**"]
rules.DG101 = "off"  # Disable missing docstrings in tests
```

### Step 6: Integrate with CI/CD

Create `.github/workflows/docstring-check.yml`:

```yaml
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
- **DG206**: Args section format validation
- **DG207**: Returns section format validation
- **DG208**: Raises section format validation
- **DG209**: Summary length validation
- **DG210**: Docstring indentation consistency

### Advanced Google Style Rules

- **DG211**: Generator functions should have Yields section
- **DG212**: Classes with public attributes should have Attributes section
- **DG213**: Complex functions should have Examples section
- **DG214**: Functions with special behavior should have Note section

## Interactive Fix Mode

DocOctopy includes an interactive mode that lets you review and approve each proposed change:

```bash
dococtopy fix . --interactive
```

### Interactive Features

- **Diff preview**: See exactly what will be changed
- **Change-by-change review**: Accept or reject each fix individually
- **Rich formatting**: Beautiful console output with colors
- **Summary statistics**: Track approved vs rejected changes

### Example Interactive Session

```
Found 3 changes for src/main.py

Change: process_data (function)
Issues: DG101
Proposed docstring:
    """Process the input data and return results.

    Args:
        data: The input data to process.
        options: Processing options.

    Returns:
        Processed data results.
    """
Show diff? [Y/n]: y
--- Original
+++ Proposed
@@ -15,6 +15,15 @@
 def process_data(data, options):
+    """Process the input data and return results.
+
+    Args:
+        data: The input data to process.
+        options: Processing options.
+
+    Returns:
+        Processed data results.
+    """
     result = []
     for item in data:
         result.append(transform(item, options))
Apply this change? [Y/n]: y
✓ Applied change for process_data

Change: validate_input (function)
Issues: DG202, DG301
Proposed docstring:
    """Validate the input parameters.

    Args:
        value: The value to validate.
        min_length: Minimum length requirement.

    Returns:
        True if valid, False otherwise.
    """
Show diff? [Y/n]: n
Apply this change? [Y/n]: n
✗ Rejected change for validate_input

Summary:
- Total changes: 3
- Applied: 1
- Rejected: 1
- Skipped: 1
```

## Canned Integration Tests

DocOctopy includes a comprehensive testing framework for LLM-powered features:

### Running Canned Tests

```bash
# Setup configuration (first time)
python tests/integration/canned/test_runner.py --setup-config

# Run all available scenarios
python tests/integration/canned/test_runner.py --all

# Run specific scenario
python tests/integration/canned/test_runner.py --scenario missing_docstrings

# Inspect a scenario (shows before/after)
python tests/integration/canned/test_runner.py --inspect missing_docstrings
```

### Available Test Scenarios

1. **Missing Docstrings**: Add docstrings to functions and classes without them
2. **Malformed Docstrings**: Fix malformed Google-style docstrings
3. **Mixed Issues**: Handle mixed docstring issues
4. **Real-World Patterns**: Real-world code patterns from actual projects
5. **Google Style Patterns**: Advanced Google style compliance scenarios

### Test Framework Features

- **Multiple LLM providers**: Ollama, OpenAI, Anthropic
- **Automated setup/cleanup**: Copies fixture files, runs tests, cleans up
- **Result validation**: Checks if tests pass/fail, counts changes
- **Interactive testing**: Supports interactive mode for manual review
- **Rich output**: Beautiful console output with colors and tables

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
DG206 = "warning"
DG207 = "warning"
DG208 = "warning"
DG209 = "info"
DG210 = "warning"
DG211 = "info"
DG212 = "info"
DG213 = "info"
DG214 = "info"
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
  --dry-run                         Show changes without applying [default: False]
  --interactive                     Accept/reject each fix interactively
  --rule TEXT                       Comma-separated rule IDs to fix
  --max-changes INTEGER             Maximum number of changes
  --llm-provider {openai,anthropic,ollama}  LLM provider [default: openai]
  --llm-model TEXT                  LLM model to use [default: gpt-4o-mini]
  --llm-base-url TEXT               Base URL for LLM provider (for Ollama, etc.)
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

### Example 3: Interactive Fix Mode

```bash
# Interactive mode with diff preview
dococtopy fix . --interactive

# Output:
# Found 3 changes for src/main.py
# 
# Change: process_data (function)
# Issues: DG101
# Show diff? [Y/n]: y
# --- Original
# +++ Proposed
# @@ -15,6 +15,15 @@
#  def process_data(data, options):
# +    """Process the input data and return results.
# +
# +    Args:
# +        data: The input data to process.
# +        options: Processing options.
# +
# +    Returns:
# +        Processed data results.
# +    """
#      result = []
#      for item in data:
#          result.append(transform(item, options))
# Apply this change? [Y/n]: y
# ✓ Applied change for process_data
```

### Example 4: CI/CD Integration

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
- **Interactive Reviewer**: Handles interactive fix workflows with diff preview

## Publishing

DocOctopy is automatically published to PyPI via GitHub Actions when a release is created.

### Manual Publishing (for maintainers)

1. **Update version** in `pyproject.toml`
2. **Build and test** the package:

   ```bash
   uv build
   ```

3. **Create a GitHub release** with tag `v0.1.2` (matching the version)
4. **GitHub Action** will automatically publish to PyPI

### PyPI Setup (one-time)

To enable automatic publishing, configure trusted publishing in PyPI:

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Navigate to "Publishing" → "Publishing tokens" → "Add a new pending publisher"
3. Configure:
   - **PyPI project name**: `dococtopy`
   - **Owner**: `CrazyBonze` (your GitHub username)
   - **Repository name**: `DocOctopy`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: (leave empty)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/CrazyBonze/DocOctopy.git
cd DocOctopy
uv sync --group dev
uv run pytest
```

### Development Workflow

We use pre-commit hooks to ensure code quality and prevent CI failures:

```bash
# Install pre-commit hooks (one-time setup)
uv run task pre-commit:install

# Run pre-commit checks manually
uv run task pre-commit:run

# Or use the convenience script
./scripts/pre-commit.sh
```

**Pre-commit checks include:**
- **Black**: Code formatting
- **isort**: Import sorting
- **MyPy**: Type checking
- **Pytest**: Fast test suite

**Available tasks:**
```bash
uv run task format          # Format code
uv run task lint            # Run linting
uv run task test:fast       # Run fast tests
uv run task test:cov        # Run tests with coverage
uv run task ci              # Run full CI pipeline
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
- ✅ Interactive fix workflows
- ✅ File writing capabilities
- ✅ Advanced Google style rules (DG211-DG214)
- ✅ Canned integration tests

### V1 (Next)

- 🔄 GitHub Action and pre-commit hooks
- 🔄 Playground UI for prompt experimentation
- 🔄 Additional Python rules (coverage thresholds, etc.)
- 🔄 Batch processing for large codebases

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
