# Assignment 11 · Worker pool

> **Lesson:** [10 · Threads and processes](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Write five small concurrency tools: a counter that stays correct under many threads, a concurrent
fetcher that never loses an error, a timeout wrapper, a worker pool built from a `Queue` and plain
threads, and a process-based `map` for CPU-bound work.

## What to write

| Name | Specification |
|---|---|
| `SafeCounter()` | `increment(amount=1)` adds to the counter, `value` (a **property**) reads it. Thread-safe: protect the update with a `threading.Lock` stored in the attribute `lock`, used as `with self.lock:` |
| `fetch_all(urls, fetch, *, max_workers=8)` | calls `fetch(url)` for every URL **concurrently** with a `ThreadPoolExecutor`. Returns a dict `{url: result}` in **input order**. If a call raises, the dict holds the **exception object** for that URL instead; the other results are not affected |
| `run_with_timeout(func, *args, timeout)` | runs `func(*args)` in a worker thread and returns its result. If it takes longer than `timeout` seconds, raise the built-in `TimeoutError("<func name> did not finish within <timeout> s")` **right away**, without waiting for `func` to finish. Exceptions of `func` propagate |
| `process_queue(items, worker, *, num_workers=4)` | a hand-made pool: put the items into a `queue.Queue`, start `num_workers` `threading.Thread`s that take items and call `worker(item)`, stop them with a sentinel, and return the list of results in **input order** (an exception object where `worker` raised). No executors here |
| `parallel_map(func, items, *, workers=2)` | `list` of `func(item)` for all items, computed in a `ProcessPoolExecutor` with `workers` processes. `func` must be importable (a module-level function, e.g. `math.factorial`) |

## Examples

```python
>>> counter = SafeCounter()
>>> threads = [threading.Thread(target=lambda: [counter.increment() for _ in range(10_000)]) for _ in range(8)]
>>> for t in threads: t.start()
>>> for t in threads: t.join()
>>> counter.value
80000

>>> def fake_fetch(url):
...     time.sleep(0.5)
...     if "bad" in url:
...         raise ConnectionError(url)
...     return len(url)
>>> fetch_all(["a.com", "bad.org", "c.net"], fake_fetch)      # about 0.5 s, not 1.5 s
{'a.com': 5, 'bad.org': ConnectionError('bad.org'), 'c.net': 5}

>>> run_with_timeout(time.sleep, 5, timeout=0.1)
Traceback (most recent call last):
TimeoutError: sleep did not finish within 0.1 s

>>> process_queue([3, 1, 2], lambda n: n * 10, num_workers=2)
[30, 10, 20]

>>> parallel_map(math.factorial, range(6))
[1, 1, 2, 6, 24, 120]
```

## Hints

<details>
<summary>Hint 1: SafeCounter and fetch_all</summary>

`self.lock = threading.Lock()` in `__init__`; the property can read the value without the lock (reading
one attribute is a single step). In `fetch_all`, submit everything first:
`futures = {url: pool.submit(fetch, url) for url in urls}`, then build the result dict from the futures
in that order. `future.exception()` returns the exception or `None`.
</details>

<details>
<summary>Hint 2: run_with_timeout</summary>

A `with ThreadPoolExecutor() as pool:` block waits for the worker when it ends, which would defeat
the timeout. Create the executor without `with`, and call `pool.shutdown(wait=False)` in a `finally`.
`future.result(timeout=...)` raises `concurrent.futures.TimeoutError` (on Python 3.10 a different class
than the built-in one): catch it and raise the built-in `TimeoutError` with the message.
</details>

<details>
<summary>Hint 3: process_queue</summary>

Put `(index, item)` pairs into the queue so every result knows where it belongs, and let each worker
write `results[index] = ...` into a list prepared as `[None] * len(items)` (each index is written by
exactly one thread, so no lock is needed). After the items, put one sentinel per worker, then `join()`
all threads.
</details>

## Check your work

```bash
pytest advanced/10-threads-and-processes/assignments/11-worker-pool -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/10-threads-and-processes/assignments/11-worker-pool/exercise.py),
then tick off assignment 11 in the [progress checklist](../../../../README.md#progress-checklist).
