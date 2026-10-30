# Assignment 10 · List statistics

> **Lesson:** [07 · Lists and tuples](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1 h

## Goal

Write the small statistics functions behind every dashboard: average, median, range, running totals,
top results. One rule applies to all of them: **never change the list you were given.** The tests check it.

## What to write

| Function | Returns |
|---|---|
| `mean(numbers)` | the average; `None` for an empty list |
| `median(numbers)` | the middle value of the sorted numbers; for an even count, the average of the two middle values; `None` for an empty list |
| `min_max(numbers)` | a tuple `(smallest, largest)`; `None` for an empty list. **Write it with a loop**, without `min()` and `max()`, for practice |
| `running_total(numbers)` | a new list where each item is the sum of all items up to that position |
| `remove_duplicates(items)` | a new list without repeated items, **keeping the order of first appearance** |
| `top_n(numbers, n)` | a new list with the `n` largest numbers, largest first |

## Examples

```python
>>> mean([1, 2, 3, 4])
2.5
>>> median([5, 1, 3])
3
>>> median([4, 1, 3, 2])
2.5
>>> min_max([4, -2, 9, 0])
(-2, 9)
>>> running_total([1, 2, 3, 4])
[1, 3, 6, 10]
>>> remove_duplicates(["b", "a", "b", "c", "a"])
['b', 'a', 'c']
>>> scores = [70, 95, 82, 61]
>>> top_n(scores, 2)
[95, 82]
>>> scores
[70, 95, 82, 61]
```

## Hints

<details>
<summary>Hint 1: empty lists</summary>

Start each of `mean`, `median` and `min_max` with a guard clause: `if not numbers: return None`.
</details>

<details>
<summary>Hint 2: median</summary>

Work on `sorted(numbers)`, a new list, so the caller's list stays as it was.
For a length `n`, the middle index is `n // 2`. If `n` is even, you need the items at `n // 2 - 1` and `n // 2`.
</details>

<details>
<summary>Hint 3: min_max with a loop</summary>

Start with `smallest = largest = numbers[0]`, then loop over the rest and update both when you find
something smaller or larger. Return them as a tuple: `return smallest, largest`.
</details>

<details>
<summary>Hint 4: remove_duplicates</summary>

An accumulator list `result = []`. Append an item only `if item not in result`.
(Lesson 08 shows a faster way to check "seen before?" with a set.)
</details>

<details>
<summary>Hint 5: top_n</summary>

`sorted(..., reverse=True)` and a slice `[:n]`. Do **not** call `numbers.sort()`; that would reorder the
caller's list.
</details>

## Check your work

```bash
pytest beginner/07-lists-and-tuples/assignments/10-list-stats -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/07-lists-and-tuples/assignments/10-list-stats/exercise.py),
then tick off assignment 10 in the [progress checklist](../../../../README.md#progress-checklist).
