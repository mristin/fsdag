"""Run the pre-commit on all the files."""

import argparse
import os
import pathlib
import subprocess
import sys


def main() -> int:
    """Execute the main routine."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--overwrite", help="Auto-heal, where possible", action="store_true"
    )
    args = parser.parse_args()

    overwrite = bool(args.overwrite)

    this_path = pathlib.Path(os.path.realpath(__file__))
    repo_root = this_path.parent

    python_files = (
        [str(pth) for pth in sorted((repo_root / "fsdag").glob("*.py"))]
        + [str(pth) for pth in sorted((repo_root / "tests").glob("*.py"))]
        + [str(this_path)]
    )

    subprocess.check_call(
        ["black", "--check"] + python_files
        if not overwrite
        else ["black"] + python_files
    )

    subprocess.check_call(["mypy"] + python_files)

    subprocess.check_call(["pylint"] + python_files)

    subprocess.check_call(
        ["coverage", "run", "--source", "fsdag", "-m", "unittest", "discover"],
        cwd=str(repo_root),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
