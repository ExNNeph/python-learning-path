"""Assignment 10 · List statistics.

Replace each `raise NotImplementedError` with your code. Never change the list you were given.
Check your work:  pytest beginner/07-lists-and-tuples/assignments/10-list-stats -v
"""


def mean(numbers):
    """Return the average of numbers, or None for an empty list."""
    raise NotImplementedError


def median(numbers):
    """Return the middle value (average of the two middle values for an even count), or None."""
    raise NotImplementedError


def min_max(numbers):
    """Return (smallest, largest) using a loop (no min()/max()), or None for an empty list."""
    raise NotImplementedError


def running_total(numbers):
    """Return a new list of cumulative sums: [1, 2, 3] -> [1, 3, 6]."""
    raise NotImplementedError


def remove_duplicates(items):
    """Return a new list without repeats, keeping the order of first appearance."""
    raise NotImplementedError


def top_n(numbers, n):
    """Return a new list with the n largest numbers, largest first."""
    raise NotImplementedError


if __name__ == "__main__":
    data = [70, 95, 82, 61, 95, 88]
    print("mean:", mean(data), "median:", median(data), "range:", min_max(data))
    print("top 3:", top_n(data, 3))
