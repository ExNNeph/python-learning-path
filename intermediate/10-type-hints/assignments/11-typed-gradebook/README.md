# Assignment 11 · Typed gradebook

> **Lesson:** [10 · Type hints](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Implement a small gradebook module **with complete type hints**. The tests check the behaviour, check that
every function is annotated, and run **mypy in strict mode** on your file. Green means: correct *and*
type-safe.

## What to write

The type definitions come first:

| Name | Definition |
|---|---|
| `Grade` | a type alias: `Literal["A", "B", "C", "D", "F"]` |
| `StudentRecord` | a `TypedDict` with `name: str` and `scores: list[float]` |
| `Scorer` | a `Protocol` with one method `score(self, answer: str) -> float` |

Then the functions and classes, each **fully annotated** (all parameters and the return type):

| Function / class | Does |
|---|---|
| `average(scores)` | the mean of an **iterable** of floats. Empty: `ValueError("no scores")` |
| `letter_grade(score)` | `"A"` for ≥ 90, `"B"` ≥ 80, `"C"` ≥ 70, `"D"` ≥ 60, else `"F"`. Return type: `Grade` |
| `parse_record(line)` | `"Ada: 91, 85.5, 78"` → `{"name": "Ada", "scores": [91.0, 85.5, 78.0]}`. No `:`, empty name or a non-number: `ValueError`. `"Ada:"` gives an empty score list |
| `best_student(records)` | the name of the student with the highest average; students without scores are ignored; `None` if nobody has scores. Return type: `str \| None` |
| `report(records)` | a dict `name → Grade` of each student's average (students without scores are left out) |
| `apply_curve(records, curve)` | **new** records with `curve` (a `Callable[[float], float]`) applied to every score, capped at `100.0`. The input stays unchanged |
| `ExactScorer(expected)` | `score(answer)`: `100.0` if the answer equals `expected` (case-insensitive, stripped), else `0.0` |
| `KeywordScorer(keywords)` | `score(answer)`: the percentage of keywords (a list of str) that appear in the lower-cased answer |
| `grade_answers(answers, scorer)` | the list of `Grade`s for each answer, scored by any `Scorer` |

`ExactScorer` and `KeywordScorer` must **not** inherit from `Scorer`; they satisfy the protocol by having the right method.

## Examples

```python
>>> average([90, 80.5])
85.25
>>> letter_grade(79.9)
'C'
>>> records = [parse_record("Ada: 91, 85.5, 78"), parse_record("Grace: 99, 98"), parse_record("Linus:")]
>>> best_student(records)
'Grace'
>>> report(records)
{'Ada': 'B', 'Grace': 'A'}
>>> apply_curve(records, lambda s: s + 5)[1]
{'name': 'Grace', 'scores': [100.0, 100.0]}
>>> grade_answers(["Paris", " paris ", "Rome"], ExactScorer("PARIS"))
['A', 'A', 'F']
>>> KeywordScorer(["loop", "iterator", "next"]).score("A for loop calls next() on an iterator")
100.0
```

## Check your work

```bash
pytest intermediate/10-type-hints/assignments/11-typed-gradebook -v
```

And run mypy yourself to see its messages directly:

```bash
mypy intermediate/10-type-hints/assignments/11-typed-gradebook/exercise.py --strict
```

## Hints

<details>
<summary>Hint 1: the type definitions</summary>

```python
from collections.abc import Callable, Iterable
from typing import Literal, Protocol, TypedDict

Grade = Literal["A", "B", "C", "D", "F"]

class StudentRecord(TypedDict):
    name: str
    scores: list[float]
```
</details>

<details>
<summary>Hint 2: average with an Iterable</summary>

An iterable may be a generator, so you cannot call `len()` on it, and you can loop over it only once.
Convert it first: `values = list(scores)`.
</details>

<details>
<summary>Hint 3: mypy and Literal</summary>

`letter_grade` must return one of the literal strings directly (`return "A"`), so mypy can see that every
path returns a `Grade`. In `apply_curve`, build new dicts with `{"name": ..., "scores": [...]}`; mypy
checks them against `StudentRecord` because of the return annotation.
</details>

## Done?

Compare with the [template solution](../../../../solutions/intermediate/10-type-hints/assignments/11-typed-gradebook/exercise.py),
then tick off assignment 11 in the [progress checklist](../../../../README.md#progress-checklist).
