# Assignment 06 · Resilience kit

> **Lesson:** [06 · Errors and resilience](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Build the toolbox that keeps a service alive when its dependencies are not: exponential backoff with
jitter, a retry helper that only retries what is worth retrying, a circuit breaker, error translation
with proper chaining, and a guard that makes an operation safe to repeat.

Time and randomness are **injected** (`sleep`, `clock`, `rng`), so the tests run in milliseconds and give
the same result every time.

## What to write

| Name | Specification |
|---|---|
| `backoff_delays(attempts, *, base=0.1, factor=2.0, maximum=5.0, rng=None)` | the list of `attempts - 1` waits between attempts: wait *i* (from 0) is `min(maximum, base * factor**i)`. With an `rng` (a `random.Random`), every wait becomes `rng.uniform(0, wait)` ("full jitter"), in order. `attempts < 1` raises `ValueError` |
| `RetryError(attempts, last)` | an exception with the attributes `attempts` and `last` (the last exception) and the message `"gave up after <attempts> attempts: <repr of last>"` |
| `retry_call(func, *, attempts=3, retry_on=TRANSIENT, base, factor, maximum, sleep=time.sleep, rng=None)` | calls `func()` and returns its result. If it raises one of `retry_on`, call `sleep(wait)` with the next wait from `backoff_delays(...)` and try again, up to `attempts` calls in total. If the exception has an attribute `retry_after` that is not `None`, sleep that long instead. After the last failed attempt, raise `RetryError` **chained** (`from`) to the last error. Exceptions not in `retry_on` propagate immediately, without a retry |
| `CircuitBreaker(failure_threshold=3, reset_timeout=30.0, clock=time.monotonic)` | see below |
| `CircuitOpenError` | given |
| `translate(mapping)` | a context manager. An exception inside the block that is an instance of a key of `mapping` (the first matching key wins) is re-raised as `mapping[key](str(error))`, **chained** to the original. Other exceptions pass through unchanged |
| `idempotent(store)` | a decorator factory. The decorated function gets a **required keyword argument** `idempotency_key` (not passed on to the function). The first call with a key runs the function and stores the result in `store` (a dict-like object). A later call with the same key returns the stored result **without calling the function**, but raises `ValueError` if the other arguments differ. A call that raises stores nothing, so it can be retried |

### The circuit breaker

| Property / method | Behaviour |
|---|---|
| `state` | `"closed"`, `"open"`, or `"half_open"` (open, and at least `reset_timeout` seconds have passed on `clock()` since it opened) |
| `call(func, *args, **kwargs)` | **open**: raise `CircuitOpenError` without calling `func`. Otherwise call `func(*args, **kwargs)`. A success returns the result, resets the failure count and closes the circuit. A failure (any `Exception`) is re-raised; it counts one consecutive failure. The circuit **opens** when the count reaches `failure_threshold`, or immediately when the failed call was the half-open trial call. Opening records the time, so the `reset_timeout` starts again |

## Examples

```python
>>> backoff_delays(8, maximum=2.0)
[0.1, 0.2, 0.4, 0.8, 1.6, 2.0, 2.0]

>>> calls = iter([ConnectionError("reset"), TimeoutError("slow"), "ok"])
>>> def flaky():
...     outcome = next(calls)
...     if isinstance(outcome, Exception):
...         raise outcome
...     return outcome
>>> retry_call(flaky, sleep=lambda s: print(f"sleeping {s:.2f} s"))
sleeping 0.10 s
sleeping 0.20 s
'ok'

>>> with translate({KeyError: LookupError, OSError: ConnectionError}):
...     {}["user-42"]
Traceback (most recent call last):
KeyError: 'user-42'

The above exception was the direct cause of the following exception:

LookupError: 'user-42'

>>> store = {}
>>> @idempotent(store)
... def charge(account, cents):
...     print(f"charging {cents} to {account}")
...     return f"receipt-{account}-{cents}"
>>> charge("ada", 500, idempotency_key="k1")
charging 500 to ada
'receipt-ada-500'
>>> charge("ada", 500, idempotency_key="k1")       # a retry: no second charge
'receipt-ada-500'
```

## Hints

<details>
<summary>Hint 1: retry_call</summary>

Compute the waits once with `backoff_delays`. Loop `for attempt in range(attempts)`, `return func()`
inside `try`, and in `except retry_on as error:` either raise the `RetryError` (last attempt) or sleep.
`except` accepts a tuple of exception classes.
</details>

<details>
<summary>Hint 2: the circuit breaker</summary>

Two attributes are enough: the number of consecutive failures and `opened_at` (the `clock()` time when it
opened, or `None` while closed). `state` is computed from them. In `call`, read the state **once** at the
start, so you know whether this call is the half-open trial.
</details>

<details>
<summary>Hint 3: translate and idempotent</summary>

`except tuple(mapping) as error:` catches all keys at once; then find the first matching key with
`isinstance`. For `idempotent`, write the wrapper as `def wrapper(*args, idempotency_key, **kwargs)`:
Python then requires the keyword and keeps it out of `kwargs`. Store `((args, kwargs), result)`.
</details>

## Check your work

```bash
pytest professional/06-errors-and-resilience/assignments/06-resilience-kit -v
```

## Done?

Compare with the [template solution](../../../../solutions/professional/06-errors-and-resilience/assignments/06-resilience-kit/exercise.py),
then tick off assignment 06 in the [progress checklist](../../../../README.md#progress-checklist).
