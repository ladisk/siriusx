#!/usr/bin/env python3
"""
Test Validation Script

This script validates that all test functions follow the required docstring format:
- "Validates:" section describing what behavior is tested
- "Synthetic Input:" section with concrete mock values
- "Prediction:" section with expected outcome

Usage:
    uv run python scripts/validate_tests.py
    uv run python scripts/validate_tests.py tests/test_unit_processing.py

Exit codes:
    0 - All tests valid
    1 - Validation errors found
"""

import ast
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Validates:",
    "Synthetic Input:",
    "Prediction:",
]


def validate_test_docstring(func_name: str, docstring: str | None) -> list[str]:
    """
    Validate a test function's docstring.

    Returns list of error messages (empty if valid).
    """
    errors = []

    if not docstring:
        errors.append(f"{func_name}: Missing docstring")
        return errors

    for section in REQUIRED_SECTIONS:
        if section not in docstring:
            errors.append(f"{func_name}: Missing '{section}' section in docstring")

    return errors


def validate_test_file(filepath: Path) -> list[str]:
    """
    Validate all test functions in a file.

    Returns list of error messages.
    """
    errors = []

    try:
        source = filepath.read_text()
        tree = ast.parse(source)
    except Exception as e:
        return [f"{filepath}: Failed to parse: {e}"]

    for node in ast.walk(tree):
        # Check functions starting with 'test_'
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            docstring = ast.get_docstring(node)
            func_errors = validate_test_docstring(node.name, docstring)
            for err in func_errors:
                errors.append(f"{filepath}:{node.lineno} - {err}")

        # Check methods in classes
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    docstring = ast.get_docstring(item)
                    func_errors = validate_test_docstring(item.name, docstring)
                    for err in func_errors:
                        errors.append(f"{filepath}:{item.lineno} - {err}")

    return errors


def main():
    # Determine which files to check
    if len(sys.argv) > 1:
        # Specific files provided
        test_files = [Path(f) for f in sys.argv[1:]]
    else:
        # Find all test files
        tests_dir = Path(__file__).parent.parent / "tests"
        test_files = list(tests_dir.glob("test_*.py"))

    if not test_files:
        print("No test files found.")
        return 0

    all_errors = []
    validated_count = 0

    for filepath in test_files:
        if not filepath.exists():
            all_errors.append(f"{filepath}: File not found")
            continue

        errors = validate_test_file(filepath)
        all_errors.extend(errors)

        if not errors:
            # Count tests in file
            source = filepath.read_text()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    validated_count += 1
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                            validated_count += 1

    # Report results
    print("=" * 60)
    print("TEST DOCSTRING VALIDATION")
    print("=" * 60)

    if all_errors:
        print(f"\nFOUND {len(all_errors)} VALIDATION ERROR(S):\n")
        for error in all_errors:
            print(f"  ERROR: {error}")
        print("\n" + "=" * 60)
        print("Required docstring format:")
        print('''
    def test_example():
        """
        Validates: <what behavior is tested>

        Synthetic Input:
            - <mock setup>

        Prediction:
            <expected outcome>
        """
''')
        return 1
    else:
        print(f"\nAll {validated_count} test(s) in {len(test_files)} file(s) have valid docstrings.")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
