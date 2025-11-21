#!/usr/bin/env bash
#
# clean.sh - Remove build and runtime artifacts
#
# This script removes temporary files generated during development,
# testing, and runtime without deleting cached market data.
#

set -e

echo "🧹 Cleaning build and runtime artifacts..."

# Get the project root (parent of scripts directory)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Remove Python cache files
echo "  Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "  Removing .pyc, .pyo, .pyd files..."
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

# Remove egg-info directories
echo "  Removing *.egg-info directories..."
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.egg" -delete 2>/dev/null || true

# Remove build directories
echo "  Removing build directories..."
rm -rf build/ 2>/dev/null || true
rm -rf dist/ 2>/dev/null || true
rm -rf wheels/ 2>/dev/null || true

# Remove pytest cache and coverage files
echo "  Removing test artifacts..."
rm -rf .pytest_cache/ 2>/dev/null || true
rm -f .coverage 2>/dev/null || true
rm -rf htmlcov/ 2>/dev/null || true

# Remove mypy cache
echo "  Removing type checker cache..."
rm -rf .mypy_cache/ 2>/dev/null || true

# Remove ruff cache
echo "  Removing linter cache..."
rm -rf .ruff_cache/ 2>/dev/null || true

echo "✅ Clean complete!"
echo ""
echo "📝 Note: Market data cache (data/) was NOT deleted."
echo "   Use scripts/clean-cached-data.sh to remove cached market data."

