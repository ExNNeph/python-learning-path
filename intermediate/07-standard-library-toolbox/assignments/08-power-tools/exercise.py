"""Assignment 08 · Power tools.

Replace each `raise NotImplementedError` with your code, using the suggested standard-library tool.
Check your work:  pytest intermediate/07-standard-library-toolbox/assignments/08-power-tools -v
"""

from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
from functools import lru_cache
from itertools import combinations, groupby
from operator import itemgetter


def top_words(text, n):
    """Return the n most common lower-cased words as (word, count) pairs."""
    raise NotImplementedError


def group_by_length(words):
    """Return a plain dict: length -> list of words in original order."""
    raise NotImplementedError


def totals_by_customer(orders):
    """Return a dict customer -> total amount, customers in alphabetical order."""
    raise NotImplementedError


def last_n(iterable, n):
    """Return the last n items as a list, storing at most n items."""
    raise NotImplementedError


def pairs(items):
    """Return all unordered pairs as a list of tuples."""
    raise NotImplementedError


def count_paths(steps):
    """Return the number of ways to climb `steps` stairs with steps of 1, 2 or 3."""
    raise NotImplementedError


def weekdays_between(start, end):
    """Return the number of Mon-Fri days from start to end (ISO strings), both included."""
    raise NotImplementedError


def duration_minutes(start, end):
    """Return the minutes between two 'HH:MM' times. end before start: ValueError."""
    raise NotImplementedError


if __name__ == "__main__":
    print(top_words("to be or not to be that is the question", 2))
    print("Ways to climb 50 stairs:", count_paths(50))
    print("Workdays in November 2026:", weekdays_between("2026-11-01", "2026-11-30"))
