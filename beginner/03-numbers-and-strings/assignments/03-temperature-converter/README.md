# Assignment 03 · Temperature converter

> **Lesson:** [03 · Numbers and strings](../../) · **Difficulty:** ⭐⭐☆☆☆ · **Time:** ~30 min

## Goal

Convert temperatures between Celsius, Fahrenheit and Kelvin, round the results so float noise
disappears, and format them nicely for display.

## What to write

| Function | Returns |
|---|---|
| `celsius_to_fahrenheit(celsius)` | °F, rounded to **1** decimal |
| `fahrenheit_to_celsius(fahrenheit)` | °C, rounded to **1** decimal |
| `celsius_to_kelvin(celsius)` | K, rounded to **2** decimals |
| `format_temperature(value, unit)` | text like `"21.5 °C"`: always 1 decimal, a space, `°`, then the unit |

The formulas:

- °F = °C × 9 / 5 + 32
- °C = (°F − 32) × 5 / 9
- K = °C + 273.15

## Examples

```python
>>> celsius_to_fahrenheit(100)
212.0
>>> celsius_to_fahrenheit(37.5)
99.5
>>> fahrenheit_to_celsius(0)
-17.8
>>> celsius_to_kelvin(-273.15)
0.0
>>> format_temperature(21.456, "C")
'21.5 °C'
>>> format_temperature(-40, "F")
'-40.0 °F'
```

## Hints

<details>
<summary>Hint 1: brackets in formulas</summary>

`fahrenheit - 32 * 5 / 9` is not the same as `(fahrenheit - 32) * 5 / 9`. Multiplication binds tighter.
</details>

<details>
<summary>Hint 2: rounding</summary>

`round(value, 1)` rounds to one decimal. Without it, `celsius_to_kelvin(0.1)` gives `273.25000000000006`.
</details>

<details>
<summary>Hint 3: formatting</summary>

`f"{value:.1f}"` always shows exactly one decimal, also for whole numbers: `-40` becomes `-40.0`.
</details>

## Check your work

```bash
pytest beginner/03-numbers-and-strings/assignments/03-temperature-converter -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/03-numbers-and-strings/assignments/03-temperature-converter/exercise.py),
then tick off assignment 03 in the [progress checklist](../../../../README.md#progress-checklist).
