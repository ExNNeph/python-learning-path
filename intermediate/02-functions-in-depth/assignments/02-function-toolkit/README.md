# Assignment 02 · Function toolkit

> **Lesson:** [02 · Functions in depth](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1.5 h

## Goal

Write small functions that **take, combine and return other functions**. You practise keyword-only
parameters, argument unpacking, dispatch tables and closures.

## What to write

| Function | Does |
|---|---|
| `format_price(amount, /, *, currency="EUR", decimals=2)` | returns e.g. `"12.50 EUR"`. `amount` is positional-only, the options keyword-only |
| `calculate(a, operator, b)` | `"+"`, `"-"`, `"*"`, `"/"` via a **dispatch dict** (no `if` chain). Unknown operator: `ValueError("unknown operator: '<op>'")` |
| `pipeline(*functions)` | returns **one** function that passes its argument through all the functions, left to right. No functions: return the argument unchanged |
| `make_multiplier(factor)` | returns a function `n → n * factor` |
| `make_counter(start=0, step=1)` | returns a function that returns `start`, then `start + step`, … on each call |
| `call_counted(func)` | returns a pair `(wrapper, calls)`: `wrapper` forwards **all** arguments to `func` and returns its result; `calls()` returns how often `wrapper` has been called |

## Examples

```python
>>> format_price(12.5)
'12.50 EUR'
>>> format_price(3, currency="USD", decimals=0)
'3 USD'
>>> calculate(6, "*", 7)
42
>>> clean = pipeline(str.strip, str.lower, lambda s: s.replace(" ", "-"))
>>> clean("  Hello World ")
'hello-world'
>>> triple = make_multiplier(3)
>>> triple(5)
15
>>> tick = make_counter(10, step=5)
>>> tick(), tick(), tick()
(10, 15, 20)
>>> wrapped, calls = call_counted(max)
>>> wrapped(3, 9, 4), wrapped([1, 2], key=abs)
(9, 2)
>>> calls()
2
```

## Hints

<details>
<summary>Hint 1: format_price</summary>

The signature from the table already does all the work of forcing positional and keyword use.
A nested f-string format gives a variable number of decimals: `f"{amount:.{decimals}f}"`.
</details>

<details>
<summary>Hint 2: pipeline</summary>

Define an inner function `run(value)` that loops over `functions` and replaces `value` with
`func(value)` each time. Return `run` (without brackets).
</details>

<details>
<summary>Hint 3: make_counter and call_counted</summary>

Both need a variable in the enclosing function that the inner function **changes**: `nonlocal`.
In `make_counter`, return the current value *before* adding the step.
`call_counted` needs **two** inner functions that share the same counter; the wrapper takes
`*args, **kwargs` and calls `func(*args, **kwargs)`.
</details>

## Check your work

```bash
pytest intermediate/02-functions-in-depth/assignments/02-function-toolkit -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/02-functions-in-depth/assignments/02-function-toolkit/exercise.py),
then tick off assignment 02 in the [progress checklist](../../../../README.md#progress-checklist).
