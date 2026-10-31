# Assignment 04 · Sorted list

> **Lesson:** [03 · The data model](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2 h

## Goal

Write a **container that keeps itself sorted**, no matter in which order you add items. It behaves
like a read-only sequence (`len`, indexing, slicing, `in`, iteration, `reversed`), and it uses binary
search from the `bisect` module, so `in` and `add` stay fast even for a million items.

## What to write

`SortedList(iterable=(), *, key=None)`: the items sorted by `key` (default: the items themselves).

| Member | Does |
|---|---|
| `add(item)` | inserts the item at the right place (equal items: after the existing ones) |
| `remove(item)` | removes one occurrence; missing: `ValueError` |
| `len(s)`, `bool(s)` | number of items, `False` when empty |
| `s[i]`, `s[a:b]` | an item, or a new `SortedList` (with the same `key`) for a slice |
| `item in s` | binary search, **no** linear scan (when `key` is `None`) |
| `iter(s)`, `reversed(s)` | ascending and descending |
| `s.index(item)`, `s.count(item)` | position of the first occurrence (missing: `ValueError`), number of occurrences |
| `s == other` | `True` for another `SortedList` with the same items in the same order. Anything else: `NotImplemented` |
| `s + other` | a new `SortedList` with the items of both (any iterable works as `other`) |
| `repr(s)` | `SortedList([1, 2, 3])` |
| `s[i] = x` | `TypeError` (assignment would break the order: do not implement `__setitem__`) |

You may use `bisect.insort`, `bisect.bisect_left` and `bisect.bisect_right`. They take a `key=`
argument only from Python 3.10 on, which is the minimum for this course anyway.

## Examples

```python
>>> s = SortedList([5, 1, 4])
>>> s.add(3)
>>> s
SortedList([1, 3, 4, 5])
>>> s[0], s[-1], s[1:3]
(1, 5, SortedList([3, 4]))
>>> 4 in s, 2 in s
(True, False)
>>> list(reversed(s))
[5, 4, 3, 1]
>>> s + [2, 6]
SortedList([1, 2, 3, 4, 5, 6])
>>> words = SortedList(["pear", "fig", "banana"], key=len)
>>> words
SortedList(['fig', 'pear', 'banana'])
```

## Hints

<details>
<summary>Hint 1: the storage</summary>

Keep a plain list, sorted at all times: `self._items = sorted(iterable, key=key)`. Every method then
relies on that invariant. `__getitem__` with a slice: build a new `SortedList` from the sliced items
(they are already sorted, sorting them again is cheap and simple).
</details>

<details>
<summary>Hint 2: binary search</summary>

`i = bisect_left(self._items, item)` is the first position where `item` could be inserted. The item
is in the list exactly when `i < len(self._items) and self._items[i] == item`. `count` is
`bisect_right(...) - bisect_left(...)`.
</details>

<details>
<summary>Hint 3: with a key</summary>

With a key, search for `key(item)` and pass `key=self._key` to the `bisect` functions. Several items
may share the same key (`"fig"` and `"bar"` both have length 3), so look through the items in the range
`bisect_left … bisect_right` for one that is `== item`.
</details>

## Check your work

```bash
pytest advanced/03-the-data-model/assignments/04-sorted-list -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/03-the-data-model/assignments/04-sorted-list/exercise.py),
then tick off assignment 04 in the [progress checklist](../../../../README.md#progress-checklist).
