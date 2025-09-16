.PHONY: install test test-watch lint format clean help

# Default target
help:
	@echo "DocOctopy Development Commands:"
	@echo "  install     Install package in development mode"
	@echo "  test        Run all tests"
	@echo "  test-watch  Run tests in watch mode"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  clean       Clean up build artifacts"
	@echo "  cli-test    Quick CLI smoke test"

install:
	uv pip install -e ".[dev]"

test:
	uv run python -m pytest -v

test-watch:
	uv run python -m pytest -v --tb=short -f

test-cov:
	uv run python -m pytest --cov=src/dococtopy --cov-report=term-missing --cov-report=html

lint:
	uv run python -m mypy src/dococtopy
	uv run python -m black --check src/ tests/
	uv run python -m isort --check-only src/ tests/

format:
	uv run python -m black src/ tests/
	uv run python -m isort src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Quick CLI test
cli-test:
	uv run python -m dococtopy.cli.main --help
	uv run python -m dococtopy.cli.main --version
	uv run python -m dococtopy.cli.main scan --help

# Run just our basic test
test-basic:
	uv run python -m pytest tests/test_cli_basic.py -v