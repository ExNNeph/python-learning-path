"""Splitting text into words: the lowest layer, it imports nothing from the package."""

import re


def words(text):
    """The words of text, lower-cased: letters, digits and apostrophes."""
    return re.findall(r"[a-z0-9']+", text.lower())


def slugify(text):
    """'Hello, World!' → 'hello-world'."""
    return "-".join(words(text.replace("'", "")))


def word_count(text):
    return len(words(text))
