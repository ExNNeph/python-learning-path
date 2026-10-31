"""The command line: the only module that reads argv, prints and exits."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .stats import top_words
from .text import slugify, word_count


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
