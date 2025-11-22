#!/usr/bin/env python3
"""
Format script to clean up trailing whitespace and empty lines with spaces.

Usage:
    uv run format           # Format files (modify in place)
    uv run format --check   # Check formatting (no modifications, exit 1 if issues found)

Behavior:
- Python/YAML/TOML/Shell/JSON/CSV files: Removes ALL trailing whitespace
- Markdown files: Preserves trailing spaces on content lines (needed for line breaks),
                  but removes spaces from empty lines

Processes: .py, .md, .yml, .yaml, .toml, .txt, .sh, .bash, .json, .csv
"""
import os
import sys
from pathlib import Path


def format_file(filepath, check_only=False):
    """
    Remove trailing whitespace and clean empty lines from a file.

    For markdown files:
    - Preserves trailing spaces on non-empty lines (needed for line breaks)
    - Removes spaces from empty lines (lines with only whitespace)

    For other files:
    - Removes all trailing whitespace

    Args:
        filepath: Path to file to format
        check_only: If True, don't modify file, just check if it needs formatting

    Returns:
        True if file needs/needed formatting, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return False

    # Split into lines, preserving line endings
    lines = original_content.splitlines(keepends=True)

    # Check if this is a markdown file
    is_markdown = filepath.suffix.lower() == '.md'

    # Process each line
    formatted_lines = []
    modified = False

    for line in lines:
        # Determine line ending
        line_ending = ''
        content = line
        if line.endswith('\r\n'):
            line_ending = '\r\n'
            content = line[:-2]
        elif line.endswith('\n'):
            line_ending = '\n'
            content = line[:-1]

        # Check if line is empty (only whitespace)
        is_empty_line = len(content.strip()) == 0

        if is_markdown:
            # For markdown: only clean empty lines with spaces
            if is_empty_line and len(content) > 0:
                # Empty line has spaces - remove them
                stripped = line_ending
                if stripped != line:
                    modified = True
                formatted_lines.append(stripped)
            else:
                # Non-empty line or already clean empty line - keep as is
                formatted_lines.append(line)
        else:
            # For non-markdown: remove all trailing whitespace
            stripped = content.rstrip() + line_ending
            if stripped != line:
                modified = True
            formatted_lines.append(stripped)

    # Write back if modified
    if modified:
        if check_only:
            # In check mode, don't modify, just return True
            return True

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(formatted_lines)
            return True
        except Exception as e:
            print(f"⚠️  Could not write {filepath}: {e}")
            return False

    return False


def should_format(filepath):
    """Check if file should be formatted based on extension."""
    extensions = {
        '.py', '.md', '.yml', '.yaml', '.toml', '.txt',
        '.sh', '.bash', '.json', '.csv'
    }
    return filepath.suffix.lower() in extensions


def main():
    """Main entry point - format all eligible files in the project."""
    # Check for --check flag
    check_only = '--check' in sys.argv

    project_root = Path(__file__).parent.parent

    # Directories to skip
    skip_dirs = {
        '.git', '.venv', '__pycache__', '.pytest_cache',
        'node_modules', '.mypy_cache', '.ruff_cache',
        'htmlcov', '.coverage', 'dist', 'build',
        '*.egg-info'
    }

    if check_only:
        print("🔍 Checking code formatting...")
    else:
        print("🎨 Formatting files...")
    print("   • Python/YAML/Shell: Remove all trailing whitespace")
    print("   • Markdown: Preserve trailing spaces on content lines, clean empty lines")
    print()

    files_need_formatting = []
    files_formatted = 0
    files_checked = 0

    # Walk through project directory
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.endswith('.egg-info')]

        for filename in files:
            filepath = Path(root) / filename

            # Skip files in data directory (generated files)
            if 'data' in filepath.parts:
                continue

            # Check if file should be formatted
            if should_format(filepath):
                files_checked += 1

                # Format or check the file
                if format_file(filepath, check_only=check_only):
                    rel_path = filepath.relative_to(project_root)
                    if check_only:
                        files_need_formatting.append(rel_path)
                        print(f"  ❌ {rel_path}")
                    else:
                        files_formatted += 1
                        print(f"  ✓ {rel_path}")

    print()
    print(f"📊 Summary:")
    print(f"   Files checked: {files_checked}")

    if check_only:
        print(f"   Files needing formatting: {len(files_need_formatting)}")
        print(f"   Files correctly formatted: {files_checked - len(files_need_formatting)}")

        if files_need_formatting:
            print()
            print("❌ Formatting check FAILED!")
            print()
            print("Run 'uv run format' to fix formatting issues.")
            return 1
        else:
            print()
            print("✅ All files are correctly formatted!")
            return 0
    else:
        print(f"   Files formatted: {files_formatted}")
        print(f"   Files unchanged: {files_checked - files_formatted}")

        if files_formatted > 0:
            print()
            print("✨ Formatting complete!")
            return 0
        else:
            print()
            print("✅ All files already formatted correctly!")
            return 0


if __name__ == "__main__":
    sys.exit(main())

