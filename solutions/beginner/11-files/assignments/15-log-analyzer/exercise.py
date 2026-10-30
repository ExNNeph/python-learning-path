"""Assignment 15 · Log analyzer: template solution."""

from pathlib import Path


def parse_line(line):
    """Return (date, time, level, message) for a valid line, or None for a blank or broken one."""
    # maxsplit=3 cuts off date, time and level and leaves the message whole,
    # spaces included. A blank line gives [], a broken one fewer than 4 parts.
    parts = line.strip().split(maxsplit=3)
    if len(parts) < 4:
        return None
    return tuple(parts)


def read_entries(path):
    """Return the parsed entries of all valid lines in the file."""
    # One helper does the file handling for both public functions below,
    # so the "open, loop, skip broken lines" logic exists only once.
    entries = []
    # with: the file is closed even if something inside the loop fails.
    # encoding="utf-8": the same result on Windows, macOS and Linux.
    with open(path, encoding="utf-8") as file:
        for line in file:          # one line at a time: fine for huge logs too
            entry = parse_line(line)
            if entry is not None:
                entries.append(entry)
    return entries
    # No try/except: a missing file raises FileNotFoundError, and the caller
    # (or the user) gets a clear traceback. There is no sensible fallback here.


def count_levels(path):
    """Return a dict mapping each level to the number of valid lines with that level."""
    counts = {}
    for _date, _time, level, _message in read_entries(path):   # _ = "not used"
        counts[level] = counts.get(level, 0) + 1
    return counts


def error_messages(path):
    """Return the messages of all ERROR lines, in file order."""
    return [message for _date, _time, level, message in read_entries(path) if level == "ERROR"]


def write_summary(log_path, summary_path):
    """Write '<LEVEL>: <count>' lines sorted by level, a blank line, then '- <message>' per error."""
    counts = count_levels(log_path)
    errors = error_messages(log_path)
    # Compute everything first, then open the output: if reading fails,
    # no half-written summary file is left behind.
    with open(summary_path, "w", encoding="utf-8") as file:
        for level in sorted(counts):
            file.write(f"{level}: {counts[level]}\n")
        file.write("\n")
        for message in errors:
            file.write(f"- {message}\n")


if __name__ == "__main__":
    # Path(__file__).parent: the folder of this script, wherever you start it from.
    here = Path(__file__).parent
    write_summary(here / "sample.log", here / "summary.txt")
    print((here / "summary.txt").read_text(encoding="utf-8"))
