# Assignment 01 · First script

> **Lesson:** [01 · How Python runs code](../../) · **Difficulty:** ⭐☆☆☆☆ · **Time:** ~20 min

## Goal

Write your first two functions and a `main()` that prints their results, then run the file as a script.
You practise the difference between `return` (hand a value back) and `print` (show it on screen).

## What to write

Open [`exercise.py`](exercise.py) and fill in the three stubs:

| Function | Returns / does |
|---|---|
| `greeting(name)` | returns the text `Hello, <name>! Welcome to Python.` |
| `seconds_in_days(days)` | returns how many seconds there are in `days` days |
| `main()` | **prints** two lines: the greeting for `"World"`, and how many seconds a week has |

## Examples

```python
>>> greeting("Ada")
'Hello, Ada! Welcome to Python.'
>>> seconds_in_days(1)
86400
>>> seconds_in_days(0)
0
```

Running the file as a script:

```text
$ python exercise.py
Hello, World! Welcome to Python.
A week has 604800 seconds.
```

## Hints

<details>
<summary>Hint 1: joining text</summary>

The `+` operator glues strings together: `"Hello, " + "Ada"` gives `"Hello, Ada"`.
Watch the spaces and the punctuation; the tests compare the text exactly.
</details>

<details>
<summary>Hint 2: seconds</summary>

A day has 24 hours, an hour has 60 minutes, a minute has 60 seconds. Multiply.
</details>

<details>
<summary>Hint 3: printing a number inside a sentence</summary>

`print` accepts several values and puts a space between them:
`print("A week has", 604800, "seconds.")` prints `A week has 604800 seconds.`
Inside `main()`, call your own functions instead of writing the numbers by hand.
</details>

## Check your work

From the repository root, with your venv active:

```bash
pytest beginner/01-how-python-runs/assignments/01-first-script -v
```

Then run your program:

```bash
python beginner/01-how-python-runs/assignments/01-first-script/exercise.py
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/01-how-python-runs/assignments/01-first-script/exercise.py)
and read its comments. Then tick off assignment 01 in the [progress checklist](../../../../README.md#progress-checklist).
