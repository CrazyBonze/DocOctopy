#!/bin/bash

# Simple test runner for initial development

echo "🐙 Running DocOctopy tests..."

# Install in development mode
echo "Installing package in development mode..."
uv pip install -e .

# Run our basic CLI test
echo ""
ARGS="$@"
echo "Running tests..."
if [ -z "$ARGS" ]; then
    uv run python -m pytest tests -v
else
    uv run python -m pytest tests -v -k "$ARGS"
fi

# Show test coverage if tests pass
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests passed! Running with coverage..."
    if [ -z "$ARGS" ]; then
        uv run python -m pytest tests --cov=src/dococtopy --cov-report=term-missing
    else
        uv run python -m pytest tests --cov=src/dococtopy --cov-report=term-missing -k "$ARGS"
    fi
else
    echo ""
    echo "❌ Tests failed. Check output above."
    exit 1
fi