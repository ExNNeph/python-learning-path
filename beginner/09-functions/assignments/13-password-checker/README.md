# Assignment 13 · Password checker

> **Lesson:** [09 · Functions](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1 h

## Goal

Build a password checker from small, focused functions that call each other. You practise default
arguments, keyword arguments, returning lists, and avoiding the mutable-default trap.

## What to write

| Function | Returns |
|---|---|
| `has_digit(text)`, `has_upper(text)`, `has_lower(text)`, `has_special(text)` | `True` if `text` contains at least one such character. *Special* = anything that is not a letter or a digit |
| `password_problems(password, min_length=8)` | a **new** list of problem messages, in this order, containing only the problems that apply |
| `strength(password, min_length=8)` | `"strong"` (no problems), `"medium"` (1 or 2 problems) or `"weak"` (3 or more) |
| `check_all(passwords, min_length=8)` | a dict `password → strength` for every password in the list |

The problem messages, in this exact order:

1. `"at least <min_length> characters"`
2. `"a digit"`
3. `"an uppercase letter"`
4. `"a lowercase letter"`
5. `"a special character"`

## Examples

```python
>>> has_special("abc!")
True
>>> password_problems("Secr3t!")
['at least 8 characters']
>>> password_problems("password")
['a digit', 'an uppercase letter', 'a special character']
>>> password_problems("Secr3t!", min_length=6)
[]
>>> strength("password")
'weak'
>>> check_all(["Tr0ub4dor&3", "hello"], min_length=10)
{'Tr0ub4dor&3': 'strong', 'hello': 'weak'}
```

## Hints

<details>
<summary>Hint 1: the has_* helpers</summary>

Loop over the characters and return `True` as soon as one matches; return `False` after the loop.
String methods help: `.isdigit()`, `.isupper()`, `.islower()`, `.isalnum()` (letter or digit).
Or, after lesson 07: `any(char.isdigit() for char in text)`.
</details>

<details>
<summary>Hint 2: password_problems</summary>

Start with `problems = []` **inside** the function and append a message for each failed check.
Use an f-string for the length message so it shows the actual `min_length`.
Do not make `problems` a default parameter: lesson 09, section 7 shows why.
</details>

<details>
<summary>Hint 3: reuse</summary>

`strength` should call `password_problems` and look at `len(...)`. `check_all` should call `strength`
and pass `min_length` on **by keyword**, so it reaches the right parameter.
</details>

## Check your work

```bash
pytest beginner/09-functions/assignments/13-password-checker -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/09-functions/assignments/13-password-checker/exercise.py),
then tick off assignment 13 in the [progress checklist](../../../../README.md#progress-checklist).
