"""Assignment 14 · Word stats CLI: template solution."""

import argparse
import json
import re
import sys
from collections import Counter

VERSION = "1.0"
WORD = re.compile(r"[\w']+")


def positive_int(text):
    """argparse type: return int(text), or raise ArgumentTypeError if it is below 1."""
    value = int(text)           # a ValueError here becomes "invalid positive_int value: 'x'"
    if value < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return value


def build_parser():
    """Return the ArgumentParser for wordstats."""
    parser = argparse.ArgumentParser(
        prog="wordstats",
        description="Count the most common words in files or standard input.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE",
                        help="files to read; none or '-' reads standard input")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("-t", "--top", type=positive_int, default=10, metavar="N",
                        help="how many words to show (default: %(default)s)")
    parser.add_argument("-m", "--min-length", type=positive_int, default=1, metavar="N",
                        help="ignore shorter words (default: %(default)s)")
    parser.add_argument("--case-sensitive", action="store_true",
                        help="count 'Python' and 'python' separately")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                        help="output format (default: %(default)s)")
    return parser


def count_words(lines, min_length=1, case_sensitive=False):
    """Return a Counter of the words ([\\w']+) in lines."""
    # A pure function: no files, no argv, no printing. Easy to test, easy to reuse.
    counts = Counter()
    for line in lines:
        if not case_sensitive:
            line = line.lower()
        counts.update(word for word in WORD.findall(line) if len(word) >= min_length)
    return counts


def format_text(counts, top):
    """Return one line per word: f"{count:>5}  {word}", most common first."""
    return "\n".join(f"{count:>5}  {word}" for word, count in counts.most_common(top))


def format_json(counts, top):
    """Return JSON with total, unique and top [[word, count], ...], indented by 2."""
    report = {
        "total": sum(counts.values()),
        "unique": len(counts),
        "top": [[word, count] for word, count in counts.most_common(top)],
    }
    return json.dumps(report, indent=2, ensure_ascii=False)


def read_lines(paths):
    """Read all lines of the files; no paths or '-' means standard input."""
    # Everything is read BEFORE any output, so a missing second file cannot leave a
    # half-printed report behind.
    lines = []
    for path in paths or ["-"]:
        if path == "-":
            lines.extend(sys.stdin)
        else:
            with open(path, encoding="utf-8") as file:
                lines.extend(file)
    return lines


def main(argv=None):
    """Run wordstats with the given arguments; return the exit code."""
    # argv=None: argparse falls back to sys.argv[1:]. Tests pass their own list.
    # Usage errors (bad --top, unknown options) make argparse exit with code 2 itself.
    args = build_parser().parse_args(argv)
    try:
        lines = read_lines(args.files)
    except OSError as error:
        # Results go to stdout, messages for humans to stderr.
        print(f"wordstats: error: cannot read {error.filename}: {error.strerror}", file=sys.stderr)
        return 1
    counts = count_words(lines, args.min_length, args.case_sensitive)
    formatter = format_json if args.format == "json" else format_text
    report = formatter(counts, args.top)
    if report:
        print(report)
    return 0


if __name__ == "__main__":
    # The only place that ends the process: everything above just returns values.
    sys.exit(main())
