# Assignment 05 · Receipt printer

> **Lesson:** [04 · Input and output](../../) · **Difficulty:** ⭐⭐☆☆☆ · **Time:** ~45 min

## Goal

Ask the user for an item, its price and a quantity, then print a small receipt with dotted, aligned lines.
You practise converting user input and keeping the logic (`format_line`) apart from the I/O (`main`).

## What to write

| Function | Returns / does |
|---|---|
| `parse_price(text)` | the price as a `float`; accepts extra spaces and a comma as decimal separator |
| `format_line(label, amount, width=24)` | one receipt line exactly `width` characters long: label on the left, amount with 2 decimals on the right, dots in between |
| `main()` | asks `Item: `, `Price: `, `Quantity: `, then prints the receipt (see below) |

## Examples

```python
>>> parse_price(" 3,50 ")
3.5
>>> parse_price("12")
12.0
>>> format_line("Coffee x3", 10.5)
'Coffee x3..........10.50'
>>> len(format_line("Coffee x3", 10.5))
24
>>> format_line("TOTAL", 7, width=12)
'TOTAL...7.00'
```

A full run (user input after the prompts):

```text
$ python exercise.py
Item: Coffee
Price: 3,50
Quantity: 3
Coffee x3..........10.50
------------------------
TOTAL..............10.50
```

The receipt is: the item line (`<item> x<quantity>` and the line total), a line of 24 dashes, and the
`TOTAL` line.

## Hints

<details>
<summary>Hint 1: parse_price</summary>

Chain the clean-up from the lesson: `.strip()`, then `.replace(",", ".")`, then `float(...)`.
</details>

<details>
<summary>Hint 2: how many dots?</summary>

First build the amount text: `f"{amount:.2f}"`. The number of dots is then
`width - len(label) - len(amount_text)`. Repeat `"."` that many times.
</details>

<details>
<summary>Hint 3: main</summary>

Read the three answers with `input(...)`. Convert the price with `parse_price` and the quantity with `int`.
Build the label with an f-string (`f"{item} x{quantity}"`) and print three lines.
The prompts must be exactly `"Item: "`, `"Price: "` and `"Quantity: "`, in that order.
</details>

## Check your work

```bash
pytest beginner/04-input-and-output/assignments/05-receipt-printer -v
```

Then try it for real:

```bash
python beginner/04-input-and-output/assignments/05-receipt-printer/exercise.py
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/04-input-and-output/assignments/05-receipt-printer/exercise.py),
then tick off assignment 05 in the [progress checklist](../../../../README.md#progress-checklist).
