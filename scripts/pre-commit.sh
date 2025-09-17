#!/bin/bash
# Pre-commit script to run formatting and linting

set -e

echo "🔍 Running pre-commit checks..."

# Run formatting
echo "📝 Formatting code..."
uv run black src/ tests/
uv run isort src/ tests/

# Run linting
echo "🔍 Linting code..."
uv run mypy src/

# Run tests
echo "🧪 Running tests..."
uv run task test:fast

echo "✅ All pre-commit checks passed!"
