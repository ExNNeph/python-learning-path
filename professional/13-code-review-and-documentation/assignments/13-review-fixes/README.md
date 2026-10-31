# Assignment 13 · Review fixes

> **Lesson:** [13 · Code review and documentation](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

A colleague's pull request adds small invoice helpers (`exercise.py`). It runs, but the review found
seven problems. Play the author: address **every** comment below. Each one names a classic from this
course; the tests check that all of them are fixed.

An invoice line is a dict `{"description": str, "price_cents": int, "qty": int}`. **All money is in
integer cents** from now on.

## The review

> **1 · `add_line` — blocking.** `lines=[]` is a mutable default: every call without `lines` shares, and
> grows, the **same** list. Also, mutating the caller's list is surprising.
> → New signature `add_line(lines, description, price_cents, qty=1)`: all but `qty` required. Return a
> **new** list with the line appended; never change the given list. The line's keys are
> `description`, `price_cents`, `qty`.

> **2 · `total` — blocking.** Floats for money: `0.1 + 0.2 != 0.3`, and invoices end up a cent off.
> → `total(lines, tax_percent=19)` returns integer **cents**: the subtotal (`price_cents * qty`, summed)
> plus tax, **rounded half up** to a whole cent, with integer arithmetic only. 1000 cents at 7 % → 1070;
> 50 cents at 7 % (53.5) → 54.

> **3 · `find_duplicates` — suggestion.** Two nested loops over all lines: O(n²), noticeably slow for big
> invoices (and `not in dups` is a third loop).
> → One pass (a `collections.Counter` works well). Return the descriptions that occur more than once,
> each once, in order of their **first appearance**. Must handle thousands of lines in well under a second.

> **4 · `parse_amount` — blocking.** The bare `except:` hides every error, and `"twelve"` silently becomes
> `0`: a wrong invoice instead of an error. Also returns a float.
> → Return **cents** as an `int`: digits, optionally followed by `.` or `,` and one or two digits
> (`"12"`, `"12.5"`, `"12,50"`, ASCII digits only); surrounding whitespace is fine. Anything else (empty, letters, a minus
> sign, three decimals, `"1.234,50"`) raises `ValueError("not an amount: <repr of the text>")`.

> **5 · `due_date` — bug.** Invoices due on a Saturday or Sunday confuse customers; the payment system
> only books on weekdays.
> → A due date that falls on a weekend moves to the following **Monday**. Negative `days` raise
> `ValueError`.

> **6 · `calc` — blocking.** `calc` is the old name of `total`, and other teams still call it. Removing
> it would break them, and keeping it silently keeps them on it forever.
> → Keep `calc(lines)` working (it returns `total(lines)`), but emit
> `DeprecationWarning("calc() is deprecated, use total()")` pointing at the **caller's** line
> (`stacklevel=2`).

> **7 · documentation — blocking.** Not a single docstring.
> → Every public function (`add_line`, `total`, `find_duplicates`, `parse_amount`, `due_date`, `calc`)
> gets a docstring, and the module gets one too. At least five functions show an **example** as a
> doctest, and all doctests pass: `python -m doctest -v exercise.py`.

## Hints

<details>
<summary>Hint 1: rounding half up with integers</summary>

`subtotal * (100 + tax_percent)` is the total in hundredths of a cent. Adding 50 and dividing with `//
100` rounds half up, without any float: `(5350 + 50) // 100 == 54`.
</details>

<details>
<summary>Hint 2: parse_amount</summary>

A regular expression `([0-9]+)(?:[.,]([0-9]{1,2}))?` with `fullmatch` accepts exactly the allowed forms
(`[0-9]`, because `\d` also matches digits of other scripts, like `١٢`).
`"5"` as decimals means 50 cents: `ljust(2, "0")`.
</details>

<details>
<summary>Hint 3: weekends and doctests</summary>

`date.weekday()` is 5 for Saturday and 6 for Sunday; Monday is `7 - weekday` days later. In a doctest,
the expected output of a date is its `repr`: `datetime.date(2026, 11, 16)`. For `calc`, wrap the call in
`warnings.catch_warnings()` inside the doctest, or leave `calc` as the one function without an example.
</details>

## Check your work

```bash
pytest professional/13-code-review-and-documentation/assignments/13-review-fixes -v
```

```bash
python -m doctest -v professional/13-code-review-and-documentation/assignments/13-review-fixes/exercise.py
```

## Done?

Compare with the [template solution](../../../../solutions/professional/13-code-review-and-documentation/assignments/13-review-fixes/exercise.py),
then tick off assignment 13 in the [progress checklist](../../../../README.md#progress-checklist).
