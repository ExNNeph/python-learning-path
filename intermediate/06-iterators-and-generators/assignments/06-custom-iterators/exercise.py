"""Assignment 06 · Custom iterators.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest intermediate/06-iterators-and-generators/assignments/06-custom-iterators -v
"""

import math


class Countdown:
    """A single-use iterator: start, start - 1, ..., 1."""

    def __init__(self, start):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class FloatRange:
    """A reusable iterable: start, start + step, ... while < stop."""

    def __init__(self, start, stop, step=1.0):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class Peekable:
    """An iterator over any iterable that can look one item ahead with peek()."""

    def __init__(self, iterable):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    def peek(self, *default):
        """Return the next item without consuming it.

        At the end: return the default if one was given, else raise StopIteration.
        (You may change the signature to peek(self, default=<marker>).)
        """
        raise NotImplementedError


if __name__ == "__main__":
    print(list(Countdown(5)))
    print(list(FloatRange(0, 2, 0.25)))
    words = Peekable(["the", "quick", "brown", "fox"])
    for word in words:
        print(word, "→ next:", words.peek(None))
