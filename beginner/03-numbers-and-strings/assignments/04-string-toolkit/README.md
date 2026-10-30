# Assignment 04 · String toolkit

> **Lesson:** [03 · Numbers and strings](../../) · **Difficulty:** ⭐⭐☆☆☆ · **Time:** ~45 min

## Goal

Build five small text helpers of the kind real programs need all the time. Each one can be written in
one or two lines with slicing and string methods. No loops and no `if` needed.

## What to write

| Function | Returns |
|---|---|
| `initials(full_name)` | the initials of a two-word name: `"ada lovelace"` → `"A.L."` |
| `is_palindrome(text)` | `True` if the text reads the same backwards, ignoring case and spaces |
| `slugify(title)` | a URL-friendly version: lower case, words joined by `-`, no extra spaces |
| `file_extension(filename)` | the part after the **last** dot: `"report.final.pdf"` → `"pdf"` |
| `mask_card_number(number)` | all but the last 4 digits replaced by `*` |

## Examples

```python
>>> initials("ada lovelace")
'A.L.'
>>> initials("Grace Hopper")
'G.H.'
>>> is_palindrome("Never odd or even")
True
>>> is_palindrome("Python")
False
>>> slugify("  Hello   World  ")
'hello-world'
>>> file_extension("archive.tar.gz")
'gz'
>>> mask_card_number("1234567812345678")
'************5678'
```

## Hints

<details>
<summary>Hint 1: initials</summary>

`"ada lovelace".split()` gives `['ada', 'lovelace']`. You can unpack it like in lesson 02:
`first, last = full_name.split()`. Then take index `[0]` of each and make it upper case.
</details>

<details>
<summary>Hint 2: is_palindrome</summary>

First build a cleaned version: remove spaces with `.replace(" ", "")` and make it lower case.
A reversed string is `text[::-1]`. A comparison like `a == b` already **is** `True` or `False`, so you
can return it directly.
</details>

<details>
<summary>Hint 3: slugify</summary>

`.split()` without an argument splits on any run of whitespace and drops empty pieces.
`"-".join(...)` puts the words back together.
</details>

<details>
<summary>Hint 4: file_extension</summary>

`.rfind(".")` returns the index of the **last** dot. Slice from one after it to the end.
(Or look up `.rsplit(".", 1)`.)
</details>

<details>
<summary>Hint 5: mask_card_number</summary>

`"*" * 3` is `"***"`. How many stars do you need? `len(number) - 4`. The last four digits are `number[-4:]`.
</details>

## Check your work

```bash
pytest beginner/03-numbers-and-strings/assignments/04-string-toolkit -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/03-numbers-and-strings/assignments/04-string-toolkit/exercise.py),
then tick off assignment 04 in the [progress checklist](../../../../README.md#progress-checklist).
