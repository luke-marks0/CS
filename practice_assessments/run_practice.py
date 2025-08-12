#!/usr/bin/env python3
"""
Practice assessments runner.

Usage examples:
  - List available problems:
      python practice_assessments/run_practice.py --list

  - Run a specific problem's tests (e.g., file_storage):
      python practice_assessments/run_practice.py --problem file_storage

Add new problems under `practice_assessments/<problem_name>/` with at least one
`test_*.py` file inside. Tests should import local modules directly, e.g.:
    from simulation import simulate_coding_framework
so they work when the problem directory is on `sys.path`.
"""

from __future__ import annotations

import argparse
import os
import sys
import unittest
from typing import List


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PRACTICE_ROOT = os.path.join(REPO_ROOT, "practice_assessments")


def find_problem_directories(base_dir: str) -> List[str]:
    problem_names: List[str] = []
    for entry in os.listdir(base_dir):
        full_path = os.path.join(base_dir, entry)
        if not os.path.isdir(full_path):
            continue
        # Consider a directory a problem if it contains at least one test_*.py
        try:
            contains_tests = any(
                fname.startswith("test_") and fname.endswith(".py")
                for fname in os.listdir(full_path)
            )
        except PermissionError:
            contains_tests = False
        if contains_tests:
            problem_names.append(entry)
    problem_names.sort()
    return problem_names


def run_unittests_for_problem(problem_name: str, pattern: str = "test_*.py", fail_fast: bool = False) -> int:
    problem_dir = os.path.join(PRACTICE_ROOT, problem_name)
    if not os.path.isdir(problem_dir):
        print(f"Error: problem directory not found: {problem_dir}")
        return 2

    # Ensure the problem directory is importable for `from simulation import ...` style imports
    sys.path.insert(0, problem_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=problem_dir, pattern=pattern, top_level_dir=problem_dir)

    runner = unittest.TextTestRunner(verbosity=2, failfast=fail_fast)
    result = runner.run(suite)
    # Return 0 on success, 1 on test failures, 2 on setup issues
    return 0 if result.wasSuccessful() else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run practice assessment tests")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available practice problems and exit",
    )
    parser.add_argument(
        "--problem",
        type=str,
        default=None,
        help="Name of the practice problem directory under practice_assessments/",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="test_*.py",
        help="Glob pattern for test discovery (default: test_*.py)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure",
    )

    args = parser.parse_args()

    problems = find_problem_directories(PRACTICE_ROOT)

    if args.list:
        if problems:
            print("Available practice problems:")
            for name in problems:
                print(f"  - {name}")
        else:
            print("No practice problems found. Add one under practice_assessments/<name>/.")
        return 0

    if not args.problem:
        if not problems:
            print("No practice problems found. Add one under practice_assessments/<name>/.")
            return 2
        print("No --problem specified. Use --list to see available problems. Example:")
        print("  python practice_assessments/run_practice.py --problem file_storage")
        return 2

    if args.problem not in problems:
        print(f"Problem '{args.problem}' not found. Use --list to see available problems.")
        return 2

    return run_unittests_for_problem(args.problem, pattern=args.pattern, fail_fast=args.fail_fast)


if __name__ == "__main__":
    sys.exit(main())


