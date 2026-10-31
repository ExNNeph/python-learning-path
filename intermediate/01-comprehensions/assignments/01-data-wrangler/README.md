# Assignment 01 · Data wrangler

> **Lesson:** [01 · Comprehensions](../../) · **Difficulty:** ⭐⭐☆☆☆ · **Time:** ~1.5 h

## Goal

You get raw data from a sign-up form and a gradebook and have to clean, reshape and summarise it.
Write **every function body as a single `return` with one comprehension or generator expression**
(the tests cannot check this, but the point of the exercise is to practise it).

## What to write

| Function | Returns |
|---|---|
| `positive_squares(numbers)` | a list of the squares of the numbers greater than 0, in order |
| `clean_names(raw)` | a list of the names with surrounding spaces removed and in title case (`"  ada lovelace "` → `"Ada Lovelace"`), **empty or blank entries dropped** |
| `email_domains(emails)` | a **set** of the lower-cased domains (the part after `@`) |
| `word_lengths(words)` | a dict `word → length` |
| `invert(mapping)` | a dict with keys and values swapped. Raises `ValueError("values are not unique")` if two keys share a value |
| `gradebook(names, scores)` | a dict `name → score`. Raises `ValueError` if the lists have different lengths |
| `passed(book, threshold=50)` | a list of the names whose score is **at least** `threshold`, sorted alphabetically |
| `all_passed(book, threshold=50)` | `True` if every score is at least `threshold` (also `True` for an empty book) |
| `flatten(grid)` | a list of all values of a list of lists, row by row |
| `transpose(grid)` | a list of lists: the columns of `grid` become its rows |

## Examples

```python
>>> positive_squares([3, -1, 0, 2])
[9, 4]
>>> clean_names(["  ada lovelace ", "", "GRACE hopper", "   "])
['Ada Lovelace', 'Grace Hopper']
>>> email_domains(["ada@Example.com", "grace@navy.mil", "linus@example.COM"])
{'example.com', 'navy.mil'}
>>> invert({"a": 1, "b": 2})
{1: 'a', 2: 'b'}
>>> gradebook(["Ada", "Grace"], [91, 78])
{'Ada': 91, 'Grace': 78}
>>> passed({"Linus": 85, "Ada": 91, "Ken": 42}, threshold=50)
['Ada', 'Linus']
>>> transpose([[1, 2, 3], [4, 5, 6]])
[[1, 4], [2, 5], [3, 6]]
```

## Hints

<details>
<summary>Hint 1: clean_names</summary>

A blank string becomes `""` after `.strip()`, and `""` is falsy. So you can filter with
`if name.strip()`. `.title()` does the capitalisation.
</details>

<details>
<summary>Hint 2: invert</summary>

Build the inverted dict with a comprehension. If some values were duplicates, the new dict is
**shorter** than the original: compare the lengths and raise.
</details>

<details>
<summary>Hint 3: gradebook and transpose</summary>

`zip(names, scores, strict=True)` raises `ValueError` by itself when the lengths differ. For
`transpose`, `zip(*grid)` gives you the columns as tuples; turn each into a list.
</details>

## Check your work

```bash
pytest intermediate/01-comprehensions/assignments/01-data-wrangler -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/01-comprehensions/assignments/01-data-wrangler/exercise.py),
then tick off assignment 01 in the [progress checklist](../../../../README.md#progress-checklist).
