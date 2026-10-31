# Assignment 02 · Resource guards

> **Lesson:** [02 · Context managers](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Write five context managers, some as classes and some as generators, that each guard a pair of
"do" and "undo": start and stop a clock, set and restore environment variables, apply or discard
changes, open and close files.

## What to write

| Name | Kind | Does |
|---|---|---|
| `Timer(clock=time.perf_counter)` | class | `with Timer() as t:` measures the block. After the block, `t.elapsed` is the duration in seconds (also when the block raised). `clock` is the function that returns the current time |
| `Suppress(*exceptions)` | class | like `contextlib.suppress`: swallows the listed exception types (and their subclasses). The caught exception is stored in `.error` (`None` if nothing was caught). Other exceptions propagate |
| `temp_env(**variables)` | `@contextmanager` | sets the given environment variables in `os.environ` for the duration of the block. A value of `None` **removes** the variable. Afterwards every variable has its old value again, or is removed if it did not exist, even if the block raised |
| `transaction(data)` | `@contextmanager` | yields a **deep copy** of the dict `data`. If the block finishes normally, `data` is updated to equal the copy (same dict object, new contents). If it raises, `data` is left untouched and the exception propagates |
| `open_all(paths, mode="r")` | `@contextmanager` | opens every file and yields the list of file objects. All are closed after the block. If opening one fails, the ones already open are closed before the error propagates |

## Examples

```python
>>> with Timer() as t:
...     total = sum(range(1_000_000))
>>> t.elapsed > 0
True

>>> with Suppress(KeyError) as s:
...     {}["missing"]
>>> s.error
KeyError('missing')

>>> import os
>>> with temp_env(DEBUG="1", HOME=None):
...     os.environ["DEBUG"], "HOME" in os.environ
('1', False)
>>> "DEBUG" in os.environ, "HOME" in os.environ
(False, True)

>>> account = {"balance": 100, "log": []}
>>> with transaction(account) as draft:
...     draft["balance"] -= 30
...     draft["log"].append("withdraw 30")
>>> account
{'balance': 70, 'log': ['withdraw 30']}
>>> with transaction(account) as draft:
...     draft["balance"] -= 500
...     raise ValueError("insufficient funds")
Traceback (most recent call last):
ValueError: insufficient funds
>>> account["balance"]
70
```

## Hints

<details>
<summary>Hint 1: Timer and Suppress</summary>

Both `__enter__` methods return `self`. In `Timer.__exit__`, compute `elapsed` with the **same** clock
you used in `__enter__`, and return `False`. In `Suppress.__exit__`, `issubclass(exc_type, self.exceptions)`
works with a tuple; remember that `exc_type` is `None` when nothing went wrong.
</details>

<details>
<summary>Hint 2: temp_env</summary>

Before changing anything, save the old values: `old = {name: os.environ.get(name) for name in variables}`.
Restoring is then the same operation as setting: for each name, a value of `None` means "delete"
(`os.environ.pop(name, None)`), anything else means "set". Put the restore in a `finally`.
</details>

<details>
<summary>Hint 3: transaction and open_all</summary>

`copy.deepcopy(data)` gives an independent copy, so changes to nested lists do not leak. To update the
**same** dict object: `data.clear()` then `data.update(draft)`. Only do that after `yield` returned
normally. For `open_all`, an `ExitStack` does all the work; `yield` inside its `with` block.
</details>

## Check your work

```bash
pytest advanced/02-context-managers/assignments/02-resource-guards -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/02-context-managers/assignments/02-resource-guards/exercise.py),
then tick off assignment 02 in the [progress checklist](../../../../README.md#progress-checklist).
