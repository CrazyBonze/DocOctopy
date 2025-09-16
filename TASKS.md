# Taskipy Tasks

This project uses [taskipy](https://github.com/taskipy/taskipy) for development workflow management. All tasks are defined in `pyproject.toml` under `[tool.taskipy.tasks]`.

## Available Tasks

### Linting Tasks

- `task lint` - Run all linting checks (black, isort, mypy)
- `task lint:black` - Check code formatting with Black
- `task lint:isort` - Check import sorting with isort
- `task lint:mypy` - Run type checking with MyPy

### Formatting Tasks

- `task format` - Format code with Black and isort
- `task format:black` - Format code with Black
- `task format:isort` - Sort imports with isort

### Testing Tasks

- `task test` - Run all tests with verbose output
- `task test:cov` - Run tests with coverage reporting
- `task test:fast` - Run tests with fast failure (stop on first failure)
- `task test:unit` - Run only unit tests
- `task test:integration` - Run only integration tests

### Build and Publish Tasks

- `task build` - Build the package with `uv build`
- `task check` - Check the built package with twine
- `task publish` - Upload the package to PyPI with twine

### Development Tasks

- `task dev` - Run format, lint, and test (full development cycle)
- `task clean` - Clean build artifacts and cache files
- `task install` - Install development dependencies
- `task install:llm` - Install development dependencies with LLM extras

### LLM Environment Tasks

- `task llm:setup` - Set up LLM environment (install DSPy and dependencies)
- `task llm:test` - Test if DSPy is available
- `task llm:clean` - Remove LLM dependencies

### CI/CD Tasks

- `task ci` - Run linting and testing with coverage (for CI)
- `task pre-commit` - Run format, lint, and fast tests (for pre-commit hooks)

## Usage Examples

```bash
# Run full development cycle
uv run task dev

# Set up LLM environment for AI features
uv run task llm:setup

# Run CI checks
uv run task ci

# Clean up and start fresh
uv run task clean
uv run task install

# Build and check package
uv run task build
uv run task check
```

## Task Dependencies

Many tasks are composed of other tasks:

- `lint` = `lint:black` + `lint:isort` + `lint:mypy`
- `format` = `format:black` + `format:isort`
- `dev` = `format` + `lint` + `test`
- `ci` = `lint` + `test:cov`
- `pre-commit` = `format` + `lint` + `test:fast`

This makes it easy to run related tasks together while still allowing granular control when needed.
