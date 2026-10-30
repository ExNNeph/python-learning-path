# Assignment 02 · Type detective

> **Lesson:** [02 · Variables and types](../../) · **Difficulty:** ⭐☆☆☆☆ · **Time:** ~30 min

## Goal

Investigate values the way Python sees them: their type, their identity, and how to convert them.
You will also write the classic swap without a temporary variable.

## What to write

Open [`exercise.py`](exercise.py) and fill in the stubs:

| Function | Returns |
|---|---|
| `type_name(value)` | the name of the value's type as a string: `"int"`, `"float"`, `"str"`, `"bool"`, `"NoneType"` |
| `describe(value)` | a sentence: `"<value> is of type <type name>"` |
| `add_numeric_strings(a, b)` | the **number** you get by adding two strings of digits, e.g. `"3"` and `"4"` → `7` |
| `swap(a, b)` | the two values in swapped order, as `b, a` |
| `same_object(a, b)` | `True` if `a` and `b` are the very same object, else `False` |

## Examples

```python
>>> type_name(42)
'int'
>>> type_name("42")
'str'
>>> describe(3.5)
'3.5 is of type float'
>>> describe(None)
'None is of type NoneType'
>>> add_numeric_strings("3", "4")
7
>>> swap(1, "a")
('a', 1)
>>> numbers = [1, 2]
>>> same_object(numbers, numbers)
True
>>> same_object(numbers, [1, 2])
False
```

## Hints

<details>
<summary>Hint 1: the name of a type</summary>

`type(42)` gives you the type object `<class 'int'>`. Every type has a `__name__` attribute:
`type(42).__name__` is `'int'`.
</details>

<details>
<summary>Hint 2: describe</summary>

You cannot `+` a number to a string. Turn the value into text with `str(value)` first, then join the pieces.
Reuse your `type_name` function.
</details>

<details>
<summary>Hint 3: "3" + "4"</summary>

`"3" + "4"` is `"34"`, because `+` on strings joins them. Convert both to `int` first.
</details>

<details>
<summary>Hint 4: swap and same_object</summary>

`return b, a` returns both values at once (as a tuple, lesson 07).
For "the very same object", lesson 02 has an operator for exactly this question.
</details>

## Check your work

```bash
pytest beginner/02-variables-and-types/assignments/02-type-detective -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/02-variables-and-types/assignments/02-type-detective/exercise.py),
then tick off assignment 02 in the [progress checklist](../../../../README.md#progress-checklist).
