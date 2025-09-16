#!/bin/bash
# Test script for DocOctopy on external projects
# Usage: ./test_external_project.sh <project_url>

set -e

PROJECT_URL=$1
PROJECT_NAME=$(basename "$PROJECT_URL" .git)

if [ -z "$PROJECT_URL" ]; then
    echo "Usage: $0 <project_url>"
    echo "Example: $0 https://github.com/pallets/flask.git"
    exit 1
fi

echo "🚀 Testing DocOctopy on external project: $PROJECT_NAME"
echo "=================================================="

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📥 Cloning project..."
git clone "$PROJECT_URL" "$PROJECT_NAME"
cd "$PROJECT_NAME"

echo "📦 Installing DocOctopy..."
pip install dococtopy

echo "🔍 Running DocOctopy scan..."
echo "=========================="

# Run scan with different formats
echo "📊 Pretty format:"
dococtopy scan . --format pretty --fail-level warning

echo ""
echo "📄 JSON format:"
dococtopy scan . --format json --output-file docstring-report.json --fail-level warning

echo ""
echo "📈 Scan summary:"
echo "Files scanned: $(jq '.summary.files_total' docstring-report.json)"
echo "Files compliant: $(jq '.summary.files_compliant' docstring-report.json)"
echo "Overall coverage: $(jq '.summary.coverage_overall' docstring-report.json | awk '{printf "%.1f%%", $1 * 100}')"

echo ""
echo "🔧 Top issues by rule:"
jq -r '.files[].findings[] | "\(.rule_id): \(.message)"' docstring-report.json | sort | uniq -c | sort -nr | head -10

echo ""
echo "📁 Files with most issues:"
jq -r '.files[] | "\(.findings | length) issues: \(.path)"' docstring-report.json | sort -nr | head -10

echo ""
echo "✅ Test completed! Report saved to: $TEMP_DIR/$PROJECT_NAME/docstring-report.json"

# Cleanup
echo ""
echo "🧹 Cleaning up..."
cd /
rm -rf "$TEMP_DIR"

echo "🎉 Done!"
