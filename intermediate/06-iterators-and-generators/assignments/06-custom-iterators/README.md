# Assignment 06 · Custom iterators

> **Lesson:** [06 · Iterators and generators](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1.5 h

## Goal

Write three classes that plug into Python's iterator protocol, so that `for`, `list()`, `sum()` and
friends work with them: a single-use **iterator**, a reusable **iterable**, and an iterator **wrapper**
that can look one item ahead.

## What to write

| Class | Does |
|---|---|
| `Countdown(start)` | an **iterator** (`__iter__` returns `self`, `__next__` does the work) that yields `start, start - 1, …, 1`. Single-use. `Countdown(0)` yields nothing |
| `FloatRange(start, stop, step=1.0)` | a **reusable iterable** like `range`, but for floats: yields `start`, `start + step`, … while the value is **less than** `stop`. `step <= 0` raises `ValueError`. `len()` returns the number of values. Iterating twice gives the same values |
| `Peekable(iterable)` | an **iterator** that wraps any iterable. `next()` works as usual. `peek()` returns the next item **without consuming it**; `peek(default)` returns `default` at the end instead of raising `StopIteration` |

## Examples

```python
>>> list(Countdown(3))
[3, 2, 1]
>>> c = Countdown(2)
>>> iter(c) is c
True
>>> list(c), list(c)
([2, 1], [])
>>> r = FloatRange(0, 1, 0.25)
>>> list(r)
[0.0, 0.25, 0.5, 0.75]
>>> len(r), sum(r)
(4, 1.5)
>>> p = Peekable("abc")
>>> p.peek()
'a'
>>> next(p), next(p)
('a', 'b')
>>> p.peek(), list(p), p.peek("end")
('c', ['c'], 'end')
```

## Hints

<details>
<summary>Hint 1: FloatRange without rounding drift</summary>

Adding `0.1` again and again accumulates float errors (`0.1 + 0.1 + 0.1` is `0.30000000000000004`).
Compute the **count** of values first: `math.ceil((stop - start) / step)` (at least 0). Then yield
`start + i * step` for `i in range(count)`. That also gives you `__len__` for free. Make `__iter__` a
generator method, so every loop gets a fresh generator.
</details>

<details>
<summary>Hint 2: Peekable</summary>

Store `self._iterator = iter(iterable)` and a "look-ahead buffer". `peek()` fetches the next item with
`next(self._iterator)` and keeps it in the buffer; `__next__` returns the buffered item first if there is
one. Use a unique marker object (`_EMPTY = object()`) to mean "buffer is empty", because `None` could be a
real item. For `peek(default)`, use a second marker as the default value of the parameter, so you can tell
"no default given" from `peek(None)`.
</details>

## Check your work

```bash
pytest intermediate/06-iterators-and-generators/assignments/06-custom-iterators -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/06-iterators-and-generators/assignments/06-custom-iterators/exercise.py),
then tick off assignment 06 in the [progress checklist](../../../../README.md#progress-checklist).
