# DocOctopy Canned Integration Tests

This directory contains canned integration tests for DocOctopy that provide a more realistic testing environment than unit tests. These tests use actual LLM models to generate docstrings and can handle the uncertainty inherent in LLM outputs.

## Overview

The canned tests provide:

- **Realistic scenarios** with actual Python code files
- **Multiple LLM providers** (Ollama, OpenAI, Anthropic)
- **Automated setup/cleanup** of test files
- **Result inspection** and validation
- **Interactive testing** capabilities

## Directory Structure

```
canned/
├── fixtures/           # Original test files (never modified)
├── scenarios/          # Working copies (created during tests)
├── results/           # Test results and logs
├── config.py          # Configuration and API key management
├── test_runner.py     # Main test framework
└── README.md          # This file
```

## Available Scenarios

### 1. Missing Docstrings (`missing_docstrings`)

- **Description**: Add docstrings to functions and classes without them
- **Rules**: DG101
- **Expected Changes**: 6
- **File**: `fixtures/missing_docstrings.py`

### 2. Malformed Docstrings (`malformed_docstrings`)

- **Description**: Fix malformed Google-style docstrings
- **Rules**: DG201, DG202, DG203, DG204
- **Expected Changes**: 5
- **File**: `fixtures/malformed_docstrings.py`

### 3. Mixed Issues (`mixed_issues`)

- **Description**: Handle mixed docstring issues
- **Rules**: DG101, DG202, DG204, DG205
- **Expected Changes**: 8
- **File**: `fixtures/mixed_issues.py`

### 4. Real-World Patterns (`real_world_patterns`)

- **Description**: Real-world code patterns from actual projects
- **Rules**: DG101, DG202, DG204
- **Expected Changes**: 10
- **File**: `fixtures/real_world_patterns.py`

## LLM Provider Configurations

### Ollama (Local)

- **Provider**: `ollama`
- **Base URL**: `http://192.168.0.132:11434`
- **Models**: `codeqwen:latest`, `llama3.1:8b`, `codellama:7b`
- **Requirements**: Local Ollama server running

### OpenAI

- **Provider**: `openai`
- **Models**: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`
- **Requirements**: `OPENAI_API_KEY` environment variable

### Anthropic

- **Provider**: `anthropic`
- **Models**: `claude-3-haiku-20240307`, `claude-3-sonnet-20240229`
- **Requirements**: `ANTHROPIC_API_KEY` environment variable

## Usage

### Quick Start

```bash
# Setup configuration (first time only)
python configure_tests.py --setup

# Run all available scenarios
python run_canned_tests.py --all

# List available scenarios
python run_canned_tests.py --list

# Run specific scenario
python run_canned_tests.py --scenario missing_docstrings

# Inspect a scenario (shows before/after)
python run_canned_tests.py --inspect missing_docstrings
```

### Configuration

The canned tests use a configuration system that supports multiple ways to set up LLM providers:

#### 1. Quick Setup Scripts (Recommended)

```bash
# Setup Ollama (for local testing)
python setup_ollama.py

# Setup OpenAI (when you have an API key)
python setup_openai.py
```

#### 2. Interactive Configuration

```bash
python configure_tests.py --setup
```

This will guide you through setting up:

- Ollama base URL and default model
- OpenAI API key and default model
- Anthropic API key and default model

#### 3. Environment Variables

```bash
# Ollama
export OLLAMA_BASE_URL="http://192.168.0.132:11434"
export OLLAMA_MODEL="codeqwen:latest"

# OpenAI
export OPENAI_API_KEY="your-openai-key"
export OPENAI_MODEL="gpt-4o-mini"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"
export ANTHROPIC_MODEL="claude-3-haiku-20240307"
```

#### 4. Configuration File

The configuration is saved to `~/.dococtopy_test_config` and contains:

- Ollama settings (base URL, models)
- OpenAI settings (API key, models)
- Anthropic settings (API key, models)

**Note**: The configuration file contains API keys and is automatically excluded from git via `.gitignore`.

### Running with Different Providers

The test runner automatically detects available API keys and runs tests with available providers. You can also modify the configurations in `config.py` to add custom providers or models.

## Test Framework Features

### Automated Setup/Cleanup

- Copies fixture files to working directory
- Runs DocOctopy on copies
- Cleans up after each test
- Preserves original fixtures

### Result Validation

- Checks if tests pass/fail
- Counts applied changes
- Compares against expected changes
- Shows detailed output

### Interactive Testing

- Supports interactive mode for manual review
- Shows before/after file contents
- Allows step-by-step inspection

### Rich Output

- Beautiful console output with colors
- Tabular results display
- Progress indicators
- Error highlighting

## Example Output

```
Running scenario: missing_docstrings
Add docstrings to functions and classes without them
Running: python -m dococtopy fix ... --rule DG101 --llm-provider ollama --llm-model codeqwen:latest
✓ missing_docstrings: 6 changes applied

┌─────────────────────────────────────────────────────────────┐
│                    Canned Test Results                      │
├─────────────┬────────┬─────────┬──────────┬─────────────────┤
│ Scenario    │ Status │ Changes │ Expected │ Provider        │
├─────────────┼────────┼─────────┼──────────┼─────────────────┤
│ missing_... │ ✅ PASS│       6 │        6 │ ollama:codeqwen │
└─────────────┴────────┴─────────┴──────────┴─────────────────┘
```

## Development Workflow

1. **Create new scenarios** by adding files to `fixtures/`
2. **Update configurations** in `config.py` for new rules or providers
3. **Run tests** to validate changes
4. **Inspect results** to verify LLM output quality
5. **Iterate** based on results

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama server is running
   - Check base URL in configuration
   - Verify model is available (`ollama list`)

2. **API Key Not Found**
   - Set environment variables for API keys
   - Check `config.py` for correct variable names

3. **Unexpected Changes**
   - LLM outputs can vary - this is expected
   - Adjust expected changes in configuration
   - Use inspection mode to review results

4. **Test Failures**
   - Check LLM provider availability
   - Verify fixture files exist
   - Review error messages in output

### Debug Mode

For detailed debugging, you can modify the test runner to add more verbose output or run individual commands manually:

```bash
# Manual test run
python -m dococtopy fix tests/integration/canned/scenarios/missing_docstrings.py \
  --rule DG101 --llm-provider ollama --llm-model codeqwen:latest \
  --llm-base-url http://192.168.0.132:11434
```

## Contributing

When adding new scenarios:

1. Create fixture file in `fixtures/`
2. Add scenario configuration to `config.py`
3. Update test runner if needed
4. Test with multiple providers
5. Document expected behavior

This framework makes it easy to test DocOctopy's interactive fix feature with real LLM models in a controlled, repeatable way.
