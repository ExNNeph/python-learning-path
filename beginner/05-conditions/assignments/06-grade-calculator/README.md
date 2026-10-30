# Assignment 06 · Grade calculator

> **Lesson:** [05 · Conditions](../../) · **Difficulty:** ⭐⭐☆☆☆ · **Time:** ~30 min

## Goal

Turn exam points into a letter grade. You practise `if` / `elif` / `else`, the order of branches,
and rejecting invalid input with a guard clause.

## What to write

| Function | Returns |
|---|---|
| `grade(points)` | the letter grade for `points` from 0 to 100 (table below), or `"invalid"` outside that range |
| `passed(points)` | `True` if the grade is A, B, C or D, otherwise `False` (also for invalid points) |
| `feedback(points)` | `"<points> points: grade <letter>"`, or `"Invalid score: <points>"` |

| Points | Grade |
|---|---|
| 90–100 | `"A"` |
| 80–89 | `"B"` |
| 70–79 | `"C"` |
| 60–69 | `"D"` |
| 0–59 | `"F"` |

Points may be floats: `89.5` is a `"B"` (there is no rounding up).

## Examples

```python
>>> grade(95)
'A'
>>> grade(89.5)
'B'
>>> grade(60)
'D'
>>> grade(101)
'invalid'
>>> passed(59)
False
>>> feedback(72)
'72 points: grade C'
>>> feedback(-5)
'Invalid score: -5'
```

## Hints

<details>
<summary>Hint 1: guard first</summary>

Start `grade` with a guard clause: if the points are below 0 or above 100, return `"invalid"` right away.
A chained comparison makes the valid range easy to read: `0 <= points <= 100`.
</details>

<details>
<summary>Hint 2: branch order</summary>

Check from the top: `>= 90`, then `>= 80`, … Each `elif` already knows that the conditions above it were
false, so you never need an upper bound like `< 90`.
</details>

<details>
<summary>Hint 3: reuse</summary>

`passed` and `feedback` should call `grade` instead of repeating the ranges. If you ever change a
boundary, you then change it in one place only.
</details>

## Check your work

```bash
pytest beginner/05-conditions/assignments/06-grade-calculator -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/05-conditions/assignments/06-grade-calculator/exercise.py),
then tick off assignment 06 in the [progress checklist](../../../../README.md#progress-checklist).
