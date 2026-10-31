# Assignment 13 · Bug hunt

> **Lesson:** [12 · Debugging](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

`exercise.py` is "finished" code written in a hurry. It contains **eleven functions with twelve bugs**. The
docstrings describe what each function *should* do, and they are correct. The code is not. Use the method
from the lesson to find and fix every bug:

1. **Reproduce**: run the tests. Each failing test shows an input and the wrong result.
2. **Isolate**: run `pytest ... -k <function_name>` to work on one function at a time.
3. **Hypothesise and test**: read the code, use `print(f"{x=}")` or `breakpoint()`, or run `pytest --pdb`.
4. **Fix the cause**: change as little as possible, so you do not introduce new bugs.

Every bug is one of the "usual suspects" from section 7 of the lesson. Try to **name** each one before
you fix it.

## What to fix

| Function | Should |
|---|---|
| `average_of_positives(numbers)` | return the average of the numbers greater than 0; `0.0` if there are none |
| `remove_short_words(words, min_length=3)` | return a **new** list without the words shorter than `min_length`; the input stays unchanged |
| `add_tag(tag, tags=None)` | return a list with the tag appended. Without `tags`, start from a **new** empty list each call |
| `make_grid(rows, cols, fill=0)` | return a `rows × cols` list of lists whose rows are **independent** |
| `find_index(items, target)` | return the index of the first `target`, or `-1` |
| `parse_config(text)` | parse `key = value` lines into a dict; split at the **first** `=`; skip blank lines and `#` comments |
| `apply_discount(price, percent)` | return the price reduced by `percent` %, rounded to 2 decimals |
| `shipping_cost(weight)` | `4.99` below 1 kg, `6.99` below 5 kg, above that `6.99` plus `0.50` per kg over 5, rounded to 2 decimals; `weight <= 0` raises `ValueError` |
| `make_multipliers(n)` | return `n` functions; the function at index `i` multiplies by `i` |
| `count_words(text)` | count words **case-insensitively**, ignoring the punctuation `.,!?;:` around them |
| `process_orders(orders)` | return the sum of the valid orders' amounts and **log a warning** (not print) for each invalid one: `skipping order <id>: <reason>` |

## Hints

<details>
<summary>Hint 1: where to start</summary>

Run all tests once and read the **names** of the failing tests: they tell you which function and which
behaviour is broken. Then work through the functions from top to bottom, one at a time.
</details>

<details>
<summary>Hint 2: process_orders</summary>

Create a module-level logger with `logger = logging.getLogger(__name__)` and call
`logger.warning("skipping order %s: %s", order_id, reason)`. The test uses pytest's built-in `caplog`
fixture to check the log records, and `capsys` to check that nothing is printed.
</details>

<details>
<summary>Hint 3: the bug names</summary>

Division by the wrong count and a missing empty case; changing a list while looping over it; a mutable
default argument; aliased rows; an off-by-one; splitting at every `=`; integer division; a missing `return`;
late binding; case sensitivity; `print` where logging belongs.
</details>

## Check your work

```bash
pytest intermediate/12-debugging/assignments/13-bug-hunt -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/12-debugging/assignments/13-bug-hunt/exercise.py),
whose comments name each bug, then tick off assignment 13 in the [progress checklist](../../../../README.md#progress-checklist).
