"""Assignment 16 · Standard library tour: template solution."""

# Imports at the top, standard library only, one per line, alphabetical.
# `import math` (not `from math import *`) keeps it obvious where pi and hypot come from.
import math
import random
import statistics
from collections import Counter
from datetime import date


def circle_area(radius):
    """Return pi * radius ** 2, rounded to 2 decimals (math)."""
    # math.pi is far more precise than a hand-typed 3.14.
    return round(math.pi * radius ** 2, 2)


def hypotenuse(a, b):
    """Return the hypotenuse of a right triangle with sides a and b, rounded to 2 decimals (math)."""
    # hypot does sqrt(a*a + b*b), and avoids overflow for huge values.
    return round(math.hypot(a, b), 2)


def days_until(date_text, today):
    """Return the days from `today` (a date) until the ISO date `date_text` (datetime)."""
    # `today` is a parameter instead of date.today() inside the function. That keeps the
    # function pure: the same inputs always give the same answer, so it can be tested.
    return (date.fromisoformat(date_text) - today).days


def weekday(date_text):
    """Return the English weekday name of the ISO date `date_text`, e.g. 'Thursday' (datetime)."""
    # %A is the full weekday name. (It follows the locale, which is English unless a
    # program changes it with the locale module.)
    return date.fromisoformat(date_text).strftime("%A")


def roll_dice(count, sides=6, seed=None):
    """Return `count` random ints from 1 to `sides`; the same seed gives the same list (random)."""
    # A private generator: seeding it does not affect random numbers anywhere else
    # in the program, which random.seed() would.
    rng = random.Random(seed)
    return [rng.randint(1, sides) for _ in range(count)]   # randint includes both ends


def summary_stats(numbers):
    """Return {'mean': ..., 'median': ..., 'stdev': ...}, each rounded to 2 decimals (statistics)."""
    # statistics.stdev is the *sample* standard deviation (divides by n - 1);
    # statistics.pstdev would be the population version.
    return {
        "mean": round(statistics.mean(numbers), 2),
        "median": round(statistics.median(numbers), 2),
        "stdev": round(statistics.stdev(numbers), 2),
    }


def most_common_letter(text):
    """Return the most frequent letter (case-insensitive); ties go to the first seen (collections)."""
    # Counter is the counting pattern from lesson 08, ready-made.
    counts = Counter(char for char in text.lower() if char.isalpha())
    letter, _count = counts.most_common(1)[0]
    return letter


if __name__ == "__main__":
    print("You rolled:", roll_dice(3))
    print("Christmas 2026 is on a", weekday("2026-12-24"))
