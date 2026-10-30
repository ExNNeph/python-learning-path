# Assignment 07 · Leap years

> **Lesson:** [05 · Conditions](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~40 min

## Goal

Write the calendar rules that every date library needs. The leap-year rule is a classic test of
combining conditions correctly with `and`, `or` and `not`.

## What to write

| Function | Returns |
|---|---|
| `is_leap_year(year)` | `True` if `year` is a leap year in the Gregorian calendar |
| `days_in_month(month, year)` | the number of days in that month (1 = January … 12 = December), or `None` for an invalid month |
| `season(month)` | `"winter"`, `"spring"`, `"summer"` or `"autumn"` (northern hemisphere, see table), or `None` for an invalid month |

**The leap-year rule:** a year is a leap year if it is divisible by 4, **except** years divisible by 100,
which are **not** leap years, **except** years divisible by 400, which **are**.

| Year | Divisible by 4? | by 100? | by 400? | Leap year? |
|---|---|---|---|---|
| 2024 | ✅ | ❌ | ❌ | ✅ |
| 2023 | ❌ | ❌ | ❌ | ❌ |
| 1900 | ✅ | ✅ | ❌ | ❌ |
| 2000 | ✅ | ✅ | ✅ | ✅ |

**Seasons:** December–February winter, March–May spring, June–August summer, September–November autumn.

## Examples

```python
>>> is_leap_year(2024)
True
>>> is_leap_year(1900)
False
>>> days_in_month(2, 2024)
29
>>> days_in_month(2, 2023)
28
>>> days_in_month(4, 2023)
30
>>> days_in_month(13, 2023) is None
True
>>> season(12)
'winter'
```

## Hints

<details>
<summary>Hint 1: "divisible by"</summary>

`year % 4 == 0` means "year is divisible by 4": the remainder is zero.
</details>

<details>
<summary>Hint 2: the leap-year condition</summary>

Say it in words first: *divisible by 4 and not divisible by 100, or divisible by 400*.
Then translate it word by word, with brackets around the `and` part to make the grouping obvious.
</details>

<details>
<summary>Hint 3: days_in_month</summary>

Start with a guard clause for months outside 1–12. February needs `is_leap_year`.
April, June, September and November have 30 days: `month in (4, 6, 9, 11)` checks all four at once.
Everything else has 31.
</details>

## Check your work

```bash
pytest beginner/05-conditions/assignments/07-leap-years -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/05-conditions/assignments/07-leap-years/exercise.py),
then tick off assignment 07 in the [progress checklist](../../../../README.md#progress-checklist).
