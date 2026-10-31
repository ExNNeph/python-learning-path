"""Assignment 14 · Word stats CLI.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest intermediate/13-command-line-programs/assignments/14-word-stats-cli -v
Run it:           python exercise.py --help
"""

import argparse
import json
import re
import sys
from collections import Counter

VERSION = "1.0"


def positive_int(text):
    """argparse type: return int(text), or raise ArgumentTypeError if it is below 1."""
    raise NotImplementedError


def build_parser():
    """Return the ArgumentParser for wordstats."""
    raise NotImplementedError


def count_words(lines, min_length=1, case_sensitive=False):
    """Return a Counter of the words ([\\w']+) in lines."""
    raise NotImplementedError


def format_text(counts, top):
    """Return one line per word: f"{count:>5}  {word}", most common first."""
    raise NotImplementedError


def format_json(counts, top):
    """Return JSON with total, unique and top [[word, count], ...], indented by 2."""
    raise NotImplementedError


def main(argv=None):
    """Run wordstats with the given arguments; return the exit code."""
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main())
