"""Assignment 02 · Mini linter.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest professional/02-code-quality-tools/assignments/02-mini-linter -v
"""

import argparse
import ast
import re
import sys
from dataclasses import dataclass

ALL_CODES = ("PLP001", "PLP002", "PLP003", "PLP004", "PLP005")


@dataclass(frozen=True, order=True)
class Finding:
    line: int
    col: int
    code: str
    message: str


def lint(source, select=None):
    """Return the sorted findings for `source`, honouring `select` and `# noqa`."""
    raise NotImplementedError


def format_finding(path, finding):
    """'path:line:col: CODE message'."""
    raise NotImplementedError


def main(argv=None):
    """Lint the files in argv, print the findings and a summary, return the exit code."""
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
