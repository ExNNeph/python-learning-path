"""Assignment 04 · Sorted list.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/03-the-data-model/assignments/04-sorted-list -v
"""

from bisect import bisect_left, bisect_right, insort


class SortedList:
    """A list that keeps its items sorted by key (default: the items themselves)."""

    def __init__(self, iterable=(), *, key=None):
        raise NotImplementedError

    def add(self, item):
        raise NotImplementedError

    def remove(self, item):
        """Remove one occurrence of item; ValueError if it is missing."""
        raise NotImplementedError

    def index(self, item):
        raise NotImplementedError

    def count(self, item):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, index):
        raise NotImplementedError

    def __contains__(self, item):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __reversed__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


if __name__ == "__main__":
    scores = SortedList([72, 95, 64])
    for score in (88, 71, 99):
        scores.add(score)
    print(scores, "median:", scores[len(scores) // 2])
