"""Word statistics, built on top of the text module."""

from collections import Counter

from .text import words


def top_words(text, n=3):
    """The n most common words as (word, count) pairs, most common first, ties alphabetically."""
    counts = Counter(words(text))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:n]
