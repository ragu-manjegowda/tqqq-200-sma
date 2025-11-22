#!/usr/bin/env python3
"""
Clean build and runtime artifacts.

Removes temporary files generated during development, testing, and runtime
without deleting cached market data.
"""
import os
import sys
import shutil
from pathlib import Path


def remove_pattern(root_dir, pattern, description):
    """Remove files or directories matching a pattern."""
    count = 0
    for path in root_dir.rglob(pattern):
        try:
            if path.is_file():
                path.unlink()
                count += 1
            elif path.is_dir():
                shutil.rmtree(path)
                count += 1
        except Exception as e:
            print(f"  ⚠️  Could not remove {path}: {e}")

    if count > 0:
        print(f"  ✓ Removed {count} {description}")
    return count


def remove_dir(dir_path, description):
    """Remove a specific directory."""
    if dir_path.exists():
        try:
            shutil.rmtree(dir_path)
            print(f"  ✓ Removed {description}")
            return True
        except Exception as e:
            print(f"  ⚠️  Could not remove {dir_path}: {e}")
    return False


def remove_file(file_path, description):
    """Remove a specific file."""
    if file_path.exists():
        try:
            file_path.unlink()
            print(f"  ✓ Removed {description}")
            return True
        except Exception as e:
            print(f"  ⚠️  Could not remove {file_path}: {e}")
    return False


def main():
    """Main entry point for the clean script."""
    project_root = Path(__file__).parent.parent

    print("🧹 Cleaning build and runtime artifacts...")
    print()

    total_removed = 0

    # Remove Python cache files
    print("Cleaning Python cache files...")
    total_removed += remove_pattern(project_root, "__pycache__", "__pycache__ directories")
    total_removed += remove_pattern(project_root, "*.pyc", ".pyc files")
    total_removed += remove_pattern(project_root, "*.pyo", ".pyo files")
    total_removed += remove_pattern(project_root, "*.pyd", ".pyd files")

    print()
    print("Cleaning egg-info directories...")
    total_removed += remove_pattern(project_root, "*.egg-info", "egg-info directories")
    total_removed += remove_pattern(project_root, "*.egg", ".egg files")

    print()
    print("Cleaning build directories...")
    remove_dir(project_root / "build", "build/")
    remove_dir(project_root / "dist", "dist/")
    remove_dir(project_root / "wheels", "wheels/")

    print()
    print("Cleaning test artifacts...")
    remove_dir(project_root / ".pytest_cache", ".pytest_cache/")
    remove_file(project_root / ".coverage", ".coverage")
    remove_dir(project_root / "htmlcov", "htmlcov/")
    remove_file(project_root / "coverage.xml", "coverage.xml")

    print()
    print("Cleaning type checker cache...")
    remove_dir(project_root / ".mypy_cache", ".mypy_cache/")

    print()
    print("Cleaning linter cache...")
    remove_dir(project_root / ".ruff_cache", ".ruff_cache/")

    print()
    print("✅ Clean complete!")
    print()
    print("📝 Note: Market data cache (data/) was NOT deleted.")
    print("   Use 'uv run clean-data' to remove cached market data.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

