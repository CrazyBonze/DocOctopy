#!/bin/bash
# Publishing script for DocOctopy

set -e

echo "🚀 DocOctopy Publishing Script"
echo "============================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run this script from the project root."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first."
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Get current version
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "📦 Current version: $VERSION"

# Build the package
echo "🔨 Building package..."
uv build

# Check the built package
echo "🔍 Checking package..."
uv tool run twine check dist/*

echo "✅ Package built successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Test the package locally:"
echo "   uv tool run twine upload --repository testpypi dist/*"
echo ""
echo "2. Create a GitHub release with tag v$VERSION"
echo "3. The GitHub Action will automatically publish to PyPI"
echo ""
echo "📁 Built files:"
ls -la dist/
