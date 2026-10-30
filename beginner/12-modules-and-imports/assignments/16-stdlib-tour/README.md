# Assignment 16 · Standard library tour

> **Lesson:** [12 · Modules and imports](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1 h

## Goal

Six small problems, each solved in one to three lines **with the right standard-library module**.
The skill you practise is not the maths; it is finding the tool that already exists, reading its
documentation, and importing it properly.

## What to write

| Function | Returns | Module to use |
|---|---|---|
| `circle_area(radius)` | the area `π·r²`, rounded to 2 decimals | `math` |
| `hypotenuse(a, b)` | the long side of a right triangle, rounded to 2 decimals | `math` |
| `days_until(date_text, today)` | the number of days from `today` (a `date`) until the ISO date in `date_text` (`"2026-12-24"`); negative if it is in the past | `datetime` |
| `weekday(date_text)` | the English weekday name of an ISO date, e.g. `"Thursday"` | `datetime` |
| `roll_dice(count, sides=6, seed=None)` | a list of `count` random ints from 1 to `sides`; the same `seed` must always give the same list | `random` |
| `summary_stats(numbers)` | a dict with `"mean"`, `"median"` and `"stdev"` (sample standard deviation), each rounded to 2 decimals | `statistics` |
| `most_common_letter(text)` | the most frequent letter (case-insensitive, letters only); on a tie, the one that appears first | `collections` |

## Examples

```python
>>> circle_area(2)
12.57
>>> hypotenuse(3, 4)
5.0
>>> from datetime import date
>>> days_until("2026-12-24", date(2026, 10, 30))
55
>>> weekday("2026-12-24")
'Thursday'
>>> roll_dice(5, seed=42) == roll_dice(5, seed=42)
True
>>> summary_stats([2, 4, 4, 4, 5, 5, 7, 9])
{'mean': 5, 'median': 4.5, 'stdev': 2.14}
>>> most_common_letter("Hello, World!")
'l'
```

## Hints

<details>
<summary>Hint 1: math</summary>

`math.pi` and `math.hypot(a, b)`. Look them up with `help(math.hypot)`.
</details>

<details>
<summary>Hint 2: dates</summary>

`from datetime import date`. `date.fromisoformat("2026-12-24")` parses the text. Subtracting two dates
gives a `timedelta`; its `.days` attribute is what you want. For the weekday, `.strftime("%A")`.
</details>

<details>
<summary>Hint 3: reproducible dice</summary>

Do not use the module-level `random.randint`: it shares one generator with the whole program.
Create your own: `rng = random.Random(seed)`, then call `rng.randint(1, sides)` `count` times.
`seed=None` gives different numbers each run, which is what you want in a real game.
</details>

<details>
<summary>Hint 4: statistics</summary>

`statistics.mean`, `statistics.median` and `statistics.stdev`. Build the dict and round each value.
</details>

<details>
<summary>Hint 5: most common letter</summary>

`collections.Counter` counts anything iterable. Feed it only the letters (`char.isalpha()`), lower-cased.
`.most_common(1)` returns a list with one `(letter, count)` tuple. On a tie, `Counter` keeps the order in
which the letters were first seen.
</details>

## Check your work

```bash
pytest beginner/12-modules-and-imports/assignments/16-stdlib-tour -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/12-modules-and-imports/assignments/16-stdlib-tour/exercise.py),
then tick off assignment 16 in the [progress checklist](../../../../README.md#progress-checklist).
