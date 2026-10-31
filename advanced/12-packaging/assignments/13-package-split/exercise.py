"""Assignment 13 · Package split.

This file is a whole program in one module. Your task (see the README): move it into a package
`wordtools/` next to this file, add a pyproject.toml, and then shrink this file to a small shim
that re-exports the package's functions and warns that it is deprecated.
Check your work:  pytest advanced/12-packaging/assignments/13-package-split -v
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

__version__ = "1.0.0"


def words(text):
    """The words of text, lower-cased: letters, digits and apostrophes."""
    return re.findall(r"[a-z0-9']+", text.lower())


def slugify(text):
    """'Hello, World!' → 'hello-world'."""
    return "-".join(words(text.replace("'", "")))


def word_count(text):
    return len(words(text))


def top_words(text, n=3):
    """The n most common words as (word, count) pairs, most common first, ties alphabetically."""
    counts = Counter(words(text))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:n]


def main(argv=None):
    parser = argparse.ArgumentParser(prog="wordtools", description="Small tools for words.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    slug = sub.add_parser("slug", help="print the slug of TEXT")
    slug.add_argument("text", nargs="+")
    for name in ("count", "top"):
        command = sub.add_parser(name, help=f"{name} the words in FILE")
        command.add_argument("file", type=Path)
    sub.choices["top"].add_argument("-n", type=int, default=3)
    args = parser.parse_args(argv)

    if args.command == "slug":
        print(slugify(" ".join(args.text)))
        return 0
    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError as error:
        print(f"wordtools: error: {error}", file=sys.stderr)
        return 1
    if args.command == "count":
        print(word_count(text))
    else:
        for word, count in top_words(text, args.n):
            print(f"{word} {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
