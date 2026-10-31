"""Assignment 07 · Lazy pipeline.

Replace each `raise NotImplementedError` with your code. All functions except take()
must be generator functions (use `yield`).
Check your work:  pytest intermediate/06-iterators-and-generators/assignments/07-lazy-pipeline -v
"""

import itertools
import random
from collections import deque


def clean_lines(lines):
    """Yield stripped lines, skipping blank lines and '#' comments."""
    raise NotImplementedError


def parse_readings(lines):
    """Yield (sensor, float_value) for each valid 'sensor,value' line; skip invalid ones."""
    raise NotImplementedError


def running_total(numbers):
    """Yield the running sum of numbers."""
    raise NotImplementedError


def chunked(iterable, size):
    """Yield lists of `size` items (the last may be shorter). size < 1: ValueError."""
    raise NotImplementedError


def sliding_window(iterable, size):
    """Yield tuples of `size` consecutive items."""
    raise NotImplementedError


def fibonacci():
    """Yield 0, 1, 1, 2, 3, 5, ... forever."""
    raise NotImplementedError


def flatten(nested):
    """Yield every non-list, non-tuple item of nested lists/tuples, depth first."""
    raise NotImplementedError


def take(iterable, n):
    """Return a list of the first n items. Must not pull more than n items."""
    raise NotImplementedError


def sensor_stream(seed=1):
    """An endless stream of fake sensor lines (provided, nothing to do here)."""
    rng = random.Random(seed)
    for i in itertools.count():
        if i % 7 == 0:
            yield "# heartbeat"
        elif i % 11 == 0:
            yield "kitchen,ERR"
        else:
            yield f"kitchen,{20 + rng.uniform(-2, 2):.1f}"


if __name__ == "__main__":
    readings = parse_readings(clean_lines(sensor_stream()))
    values = (value for _, value in readings)
    averages = (round(sum(window) / len(window), 2) for window in sliding_window(values, 3))
    print("First 10 moving averages of an endless stream:")
    print(take(averages, 10))
