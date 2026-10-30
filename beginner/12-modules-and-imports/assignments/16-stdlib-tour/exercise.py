"""Assignment 16 · Standard library tour.

Add the imports you need at the top, then replace each `raise NotImplementedError`.
Check your work:  pytest beginner/12-modules-and-imports/assignments/16-stdlib-tour -v
"""

# Your imports go here, e.g.:  import math


def circle_area(radius):
    """Return pi * radius ** 2, rounded to 2 decimals (math)."""
    raise NotImplementedError


def hypotenuse(a, b):
    """Return the hypotenuse of a right triangle with sides a and b, rounded to 2 decimals (math)."""
    raise NotImplementedError


def days_until(date_text, today):
    """Return the days from `today` (a date) until the ISO date `date_text` (datetime)."""
    raise NotImplementedError


def weekday(date_text):
    """Return the English weekday name of the ISO date `date_text`, e.g. 'Thursday' (datetime)."""
    raise NotImplementedError


def roll_dice(count, sides=6, seed=None):
    """Return `count` random ints from 1 to `sides`; the same seed gives the same list (random)."""
    raise NotImplementedError


def summary_stats(numbers):
    """Return {'mean': ..., 'median': ..., 'stdev': ...}, each rounded to 2 decimals (statistics)."""
    raise NotImplementedError


def most_common_letter(text):
    """Return the most frequent letter (case-insensitive); ties go to the first seen (collections)."""
    raise NotImplementedError


if __name__ == "__main__":
    print("You rolled:", roll_dice(3))
    print("Christmas 2026 is on a", weekday("2026-12-24"))
