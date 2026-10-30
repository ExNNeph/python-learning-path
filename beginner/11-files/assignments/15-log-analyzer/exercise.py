"""Assignment 15 · Log analyzer.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/11-files/assignments/15-log-analyzer -v
"""

from pathlib import Path


def parse_line(line):
    """Return (date, time, level, message) for a valid line, or None for a blank or broken one."""
    raise NotImplementedError


def count_levels(path):
    """Return a dict mapping each level to the number of valid lines with that level."""
    raise NotImplementedError


def error_messages(path):
    """Return the messages of all ERROR lines, in file order."""
    raise NotImplementedError


def write_summary(log_path, summary_path):
    """Write '<LEVEL>: <count>' lines sorted by level, a blank line, then '- <message>' per error."""
    raise NotImplementedError


if __name__ == "__main__":
    # Path(__file__).parent: the folder of this script, wherever you start it from.
    here = Path(__file__).parent
    write_summary(here / "sample.log", here / "summary.txt")
    print((here / "summary.txt").read_text(encoding="utf-8"))
