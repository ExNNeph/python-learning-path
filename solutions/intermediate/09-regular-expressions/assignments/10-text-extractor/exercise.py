"""Assignment 10 · Text extractor: template solution."""

import re

# Named, compiled patterns: the name says WHAT the pattern is for, the comment or
# re.VERBOSE layout says HOW it works. Each function then reads like plain Python.

# local part: letters, digits and . _ % + -   |  domain: labels joined by dots, ending in .tld
EMAIL = re.compile(r"[\w.%+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}")

USERNAME = re.compile(r"[A-Za-z]\w{2,15}")          # used with fullmatch: 3..16 characters

GERMAN_DATE = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")

LOG_LINE = re.compile(r"""
    (?P<date>\d{4}-\d{2}-\d{2})\s+
    (?P<time>\d{2}:\d{2}:\d{2})\s+
    \[(?P<level>[A-Z]+)\]\s+
    (?P<source>\w+):\s+
    (?P<message>.*)
""", re.VERBOSE)

HASHTAG = re.compile(r"#(\w+)")                     # one group: findall returns just the word

WHITESPACE = re.compile(r"\s+")

# four blocks of four digits, each optionally followed by ONE space or dash
CARD_NUMBER = re.compile(r"\b(\d{4})[ -]?(\d{4})[ -]?(\d{4})[ -]?(\d{4})\b")


def find_emails(text):
    """Return all email addresses in text, in order."""
    # No capturing groups in EMAIL (only (?:...)), so findall returns whole matches.
    return EMAIL.findall(text)


def is_valid_username(name):
    """Return True if name is 3-16 letters/digits/underscores, starting with a letter."""
    # fullmatch, not search: "a!bc" must fail even though "bc" alone looks fine.
    return USERNAME.fullmatch(name) is not None


def dates_to_iso(text):
    """Rewrite every DD.MM.YYYY date as YYYY-MM-DD."""
    return GERMAN_DATE.sub(r"\3-\2-\1", text)


def parse_log_line(line):
    """Return {'date', 'time', 'level', 'source', 'message'} or None."""
    match = LOG_LINE.fullmatch(line.strip())
    return match.groupdict() if match else None


def hashtags(text):
    """Return the lower-cased hashtags without '#', unique, in order of first appearance."""
    # dict.fromkeys keeps the first occurrence of each key, in order: an ordered "set".
    return list(dict.fromkeys(tag.lower() for tag in HASHTAG.findall(text)))


def squash_whitespace(text):
    """Replace every run of whitespace by one space and strip the ends."""
    return WHITESPACE.sub(" ", text).strip()


def mask_card_numbers(text):
    """Replace 16-digit card numbers by '**** **** **** ' + their last four digits."""
    return CARD_NUMBER.sub(r"**** **** **** \4", text)


if __name__ == "__main__":
    sample = """2026-10-31 14:30:05 [ERROR] db: connection lost for ada@example.org
    Paid with 4111 1111 1111 1234 on 31.10.2026   #Billing #urgent #billing"""
    print(parse_log_line(sample.splitlines()[0]))
    print(find_emails(sample))
    print(hashtags(sample))
    print(squash_whitespace(mask_card_numbers(dates_to_iso(sample))))
