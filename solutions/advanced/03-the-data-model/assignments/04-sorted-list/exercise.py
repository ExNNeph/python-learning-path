"""Assignment 04 · Sorted list: template solution."""

from bisect import bisect_left, bisect_right, insort


class SortedList:
    """A list that keeps its items sorted by key (default: the items themselves).

    Invariant: self._items is sorted by self._key at all times. Every method relies on it,
    and no method may break it; that is why there is no __setitem__.
    """

    def __init__(self, iterable=(), *, key=None):
        self._key = key
        self._items = sorted(iterable, key=key)

    def _range(self, item):
        """The slice of positions whose key equals item's key: O(log n)."""
        k = item if self._key is None else self._key(item)
        lo = bisect_left(self._items, k, key=self._key)
        hi = bisect_right(self._items, k, key=self._key)
        return lo, hi

    def _find(self, item):
        lo, hi = self._range(item)
        for i in range(lo, hi):        # several items may share a key: compare them for real
            if self._items[i] == item:
                return i
        return -1

    def add(self, item):
        insort(self._items, item, key=self._key)    # bisect_right: equal items go after existing ones

    def remove(self, item):
        i = self._find(item)
        if i < 0:
            raise ValueError(f"{item!r} not in SortedList")
        del self._items[i]

    def index(self, item):
        i = self._find(item)
        if i < 0:
            raise ValueError(f"{item!r} not in SortedList")
        return i

    def count(self, item):
        lo, hi = self._range(item)
        return sum(1 for i in range(lo, hi) if self._items[i] == item)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return SortedList(self._items[index], key=self._key)
        return self._items[index]

    def __contains__(self, item):
        return self._find(item) >= 0

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __eq__(self, other):
        if not isinstance(other, SortedList):
            return NotImplemented
        return self._items == other._items

    __hash__ = None                    # mutable (add/remove): explicitly unhashable

    def __add__(self, other):
        return SortedList([*self._items, *other], key=self._key)

    def __repr__(self):
        return f"SortedList({self._items!r})"


if __name__ == "__main__":
    scores = SortedList([72, 95, 64])
    for score in (88, 71, 99):
        scores.add(score)
    print(scores, "median:", scores[len(scores) // 2])
