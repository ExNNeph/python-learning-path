"""Assignment 10 · Text extractor.

Define your patterns as module-level constants with re.compile, then replace each
`raise NotImplementedError` with your code.
Check your work:  pytest intermediate/09-regular-expressions/assignments/10-text-extractor -v
"""

import re


def find_emails(text):
    """Return all email addresses in text, in order."""
    raise NotImplementedError


def is_valid_username(name):
    """Return True if name is 3-16 letters/digits/underscores, starting with a letter."""
    raise NotImplementedError


def dates_to_iso(text):
    """Rewrite every DD.MM.YYYY date as YYYY-MM-DD."""
    raise NotImplementedError


def parse_log_line(line):
    """Return {'date', 'time', 'level', 'source', 'message'} or None."""
    raise NotImplementedError


def hashtags(text):
    """Return the lower-cased hashtags without '#', unique, in order of first appearance."""
    raise NotImplementedError


def squash_whitespace(text):
    """Replace every run of whitespace by one space and strip the ends."""
    raise NotImplementedError


def mask_card_numbers(text):
    """Replace 16-digit card numbers by '**** **** **** ' + their last four digits."""
    raise NotImplementedError


if __name__ == "__main__":
    sample = """2026-10-31 14:30:05 [ERROR] db: connection lost for ada@example.org
    Paid with 4111 1111 1111 1234 on 31.10.2026   #Billing #urgent #billing"""
    print(parse_log_line(sample.splitlines()[0]))
    print(find_emails(sample))
    print(hashtags(sample))
    print(squash_whitespace(mask_card_numbers(dates_to_iso(sample))))
