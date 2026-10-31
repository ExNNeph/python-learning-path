# Assignment 01 · Decorator kit

> **Lesson:** [01 · Decorators](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Build four decorators that you will meet again in real projects: a call counter, a cache, a retry
helper and a command registry. Together they cover wrapping, state, decorators with arguments and
decorators that work with **and** without brackets.

## What to write

| Decorator | Does |
|---|---|
| `@count_calls` | counts the calls in an attribute `calls` on the decorated function (starts at `0`) |
| `@memoize` | caches results by the **positional** arguments. The decorated function gets a `cache` attribute (the dict) and a `cache_clear()` function that empties it |
| `@retry(times, *, exceptions=(Exception,))` | calls the function up to `times` times while it raises one of `exceptions`. Returns the first successful result; if all attempts fail, re-raises the **last** exception. Other exceptions are not retried. `times` below 1: `ValueError` (raised when the decorator is created) |
| `@command` / `@command(name="...")` | stores the function in the module dict `COMMANDS` under `name` (default: the function's name) and returns the function **unchanged** |

Every wrapper must keep the decorated function's name and docstring (`functools.wraps`).

## Examples

```python
>>> @count_calls
... def ping():
...     """Answer."""
...     return "pong"
>>> ping(), ping(), ping.calls, ping.__name__, ping.__doc__
('pong', 'pong', 2, 'ping', 'Answer.')

>>> @memoize
... def square(n):
...     print("computing", n)
...     return n * n
>>> square(4)
computing 4
16
>>> square(4)          # from the cache: no "computing"
16
>>> square.cache
{(4,): 16}

>>> attempts = []
>>> @retry(3, exceptions=(ConnectionError,))
... def flaky():
...     attempts.append(1)
...     if len(attempts) < 3:
...         raise ConnectionError("try again")
...     return "connected"
>>> flaky(), len(attempts)
('connected', 3)

>>> @command
... def hello(): ...
>>> @command(name="bye")
... def goodbye(): ...
>>> sorted(COMMANDS)
['bye', 'hello']
```

## Hints

<details>
<summary>Hint 1: count_calls and memoize</summary>

Set the attributes on the **wrapper** after defining it: `wrapper.calls = 0`, `wrapper.cache = cache`,
`wrapper.cache_clear = cache.clear`. Inside the wrapper, `wrapper.calls += 1` works because by the time
the wrapper runs, the name `wrapper` exists in the enclosing function.
</details>

<details>
<summary>Hint 2: retry</summary>

Three levels: `retry(times, ...)` → `decorator(func)` → `wrapper(*args, **kwargs)`. Validate `times` in
the outermost level. In the wrapper, loop `times` times with a `try` / `except exceptions as error`,
remember the error, and `raise` it after the loop. `except` accepts a **tuple** of exception classes.
</details>

<details>
<summary>Hint 3: command with optional brackets</summary>

`def command(func=None, *, name=None)`. Write an inner `decorator(f)` that registers and returns `f`.
If `func` is `None` you were called with brackets: return `decorator`. Otherwise return `decorator(func)`.
</details>

## Check your work

```bash
pytest advanced/01-decorators/assignments/01-decorator-kit -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/01-decorators/assignments/01-decorator-kit/exercise.py),
then tick off assignment 01 in the [progress checklist](../../../../README.md#progress-checklist).
