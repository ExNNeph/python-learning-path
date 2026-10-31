# Assignment 08 · Power tools

> **Lesson:** [07 · The standard library toolbox](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1.5 h

## Goal

Eight everyday problems. Each one has a tool in the standard library that solves it in a few lines.
Your job is to **recognise which one** and use it. The table names the suggested tool; try to find the
solution in the lesson before you look anything up.

## What to write

| Function | Returns | Tool |
|---|---|---|
| `top_words(text, n)` | the `n` most common words as `(word, count)` pairs, most common first. Words are the lower-cased results of `text.split()` | `Counter` |
| `group_by_length(words)` | a **plain dict** `length → list of words` in their original order | `defaultdict` |
| `totals_by_customer(orders)` | `orders` is a list of dicts with `"customer"` and `"amount"`. Returns a dict `customer → total amount`, customers in alphabetical order | `sorted` + `groupby` + `itemgetter` |
| `last_n(iterable, n)` | a list of the last `n` items of any iterable, without storing more than `n` | `deque(maxlen=…)` |
| `pairs(items)` | a list of all unordered pairs as tuples, in input order | `combinations` |
| `count_paths(steps)` | the number of ways to climb `steps` stairs taking 1, 2 or 3 steps at a time (`0` stairs: 1 way; negative: 0 ways). Must handle `steps=200` instantly | `@lru_cache` |
| `weekdays_between(start, end)` | the number of Monday-to-Friday days from `start` to `end`, **both included**. Both are ISO date strings (`"2026-11-02"`). `end` before `start`: `0` | `date`, `timedelta` |
| `duration_minutes(start, end)` | minutes between two `"HH:MM"` times on the same day. `end` before `start`: `ValueError` | `datetime.strptime` |

## Examples

```python
>>> top_words("the cat and The hat and THE bat", 2)
[('the', 3), ('and', 2)]
>>> group_by_length(["hi", "tea", "go", "cup"])
{2: ['hi', 'go'], 3: ['tea', 'cup']}
>>> totals_by_customer([{"customer": "grace", "amount": 10}, {"customer": "ada", "amount": 30}, {"customer": "ada", "amount": 5}])
{'ada': 35, 'grace': 10}
>>> last_n(range(1_000_000), 3)
[999997, 999998, 999999]
>>> pairs("ABC")
[('A', 'B'), ('A', 'C'), ('B', 'C')]
>>> count_paths(4)
7
>>> weekdays_between("2026-10-30", "2026-11-02")
2
>>> duration_minutes("09:15", "11:00")
105
```

(For `count_paths(4)`: 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2, 1+3, 3+1. Each way starts with a step of
1, 2 or 3, followed by a way to climb the rest: `count_paths(n) = count_paths(n-1) + count_paths(n-2) + count_paths(n-3)`.)

## Hints

<details>
<summary>Hint 1: count_paths</summary>

Write the recursive formula above with two base cases (`steps == 0` and `steps < 0`), then put
`@lru_cache(maxsize=None)` (or `@cache`) on the line above `def`. Without the cache, `count_paths(200)`
would need more calls than there are atoms on Earth. The tests check that the function has a cache
before they call it with big numbers.
</details>

<details>
<summary>Hint 2: totals_by_customer</summary>

`key = itemgetter("customer")`. Sort with that key, then
`{customer: sum(o["amount"] for o in group) for customer, group in groupby(sorted_orders, key=key)}`.
</details>

<details>
<summary>Hint 3: dates and times</summary>

`date.fromisoformat(text)` parses ISO dates. Walk from start to end with `+ timedelta(days=1)` and count
days whose `.weekday()` is below 5. For the times, `datetime.strptime(text, "%H:%M")` and subtract:
a `timedelta` has `.total_seconds()`.
</details>

## Check your work

```bash
pytest intermediate/07-standard-library-toolbox/assignments/08-power-tools -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/07-standard-library-toolbox/assignments/08-power-tools/exercise.py),
then tick off assignment 08 in the [progress checklist](../../../../README.md#progress-checklist).
