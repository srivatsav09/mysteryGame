"""Test runner script with detailed output"""
import sys
import pytest


def run_tests():
    """Run all tests with coverage"""
    print("=" * 70)
    print("Running Mystery Game Test Suite")
    print("=" * 70)
    print()

    # Run pytest with verbose output and coverage
    args = [
        "-v",                    # Verbose
        "--tb=short",           # Short traceback format
        "--color=yes",          # Colored output
        "-p", "no:warnings",    # Disable warnings
        "tests/",               # Test directory
    ]

    exit_code = pytest.main(args)

    print()
    print("=" * 70)
    if exit_code == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 70)

    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
