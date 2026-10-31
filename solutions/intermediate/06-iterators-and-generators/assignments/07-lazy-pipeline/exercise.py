"""Assignment 07 · Lazy pipeline: template solution."""

import itertools
import random
from collections import deque


def clean_lines(lines):
    """Yield stripped lines, skipping blank lines and '#' comments."""
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


def parse_readings(lines):
    """Yield (sensor, float_value) for each valid 'sensor,value' line; skip invalid ones."""
    for line in lines:
        parts = line.split(",")
        if len(parts) != 2:
            continue
        sensor, text = parts
        try:
            value = float(text)        # the only line that can fail: keep the try tiny
        except ValueError:
            continue
        yield sensor, value


def running_total(numbers):
    """Yield the running sum of numbers."""
    total = 0
    for number in numbers:
        total += number
        yield total
    # (itertools.accumulate(numbers) does the same; writing it once shows how.)


def chunked(iterable, size):
    """Yield lists of `size` items (the last may be shorter). size < 1: ValueError."""
    if size < 1:
        # Note: this runs on the first next(), not when chunked() is called (lesson 06, §7).
        raise ValueError("size must be at least 1")
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []                 # a NEW list: the yielded one now belongs to the caller
    if chunk:
        yield chunk


def sliding_window(iterable, size):
    """Yield tuples of `size` consecutive items."""
    # A deque with maxlen drops the oldest item on every append once it is full.
    window = deque(maxlen=size)
    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield tuple(window)        # a tuple snapshot, so later appends don't change it


def fibonacci():
    """Yield 0, 1, 1, 2, 3, 5, ... forever."""
    a, b = 0, 1
    while True:                        # infinite: the consumer decides when to stop
        yield a
        a, b = b, a + b


def flatten(nested):
    """Yield every non-list, non-tuple item of nested lists/tuples, depth first."""
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)   # recursion: hand out everything the inner call yields
        else:
            yield item


def take(iterable, n):
    """Return a list of the first n items. Must not pull more than n items."""
    # islice stops after n items without pulling an extra one.
    return list(itertools.islice(iterable, n))


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
