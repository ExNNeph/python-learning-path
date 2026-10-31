# Assignment 12 · Async crawler

> **Lesson:** [11 · asyncio](../../) · **Difficulty:** ⭐⭐⭐⭐⭐ · **Time:** ~3 h

## Goal

Build the async toolkit of a web crawler and then the crawler itself. To keep the tests fast and
offline, the "network" is simulated: every function receives the async function it should call
(`fetch`, `get_links`), and the tests pass in fakes that `await asyncio.sleep(...)`.

## What to write

All functions are `async def`, except where noted.

| Name | Specification |
|---|---|
| `fetch_all(urls, fetch, *, limit=5)` | awaits `fetch(url)` for all URLs **concurrently**, but never more than `limit` at the same time (`asyncio.Semaphore`). Returns `{url: result}` in input order; a call that raised gives the **exception object** instead |
| `first_completed(*coroutines, timeout=None)` | runs all coroutines concurrently and returns the result of the **first** one to finish. All others are **cancelled**. If the first one to finish raised, re-raise its exception. If nothing finishes within `timeout` seconds: cancel everything and raise the built-in `TimeoutError` |
| `retry(func, *args, attempts=3, delay=0.1)` | awaits `func(*args)`; if it raises, waits `delay`, then `2 * delay`, `4 * delay`, … (with `asyncio.sleep`) and tries again, at most `attempts` times in total. Returns the first success; re-raises the last exception |
| `ticker(count, interval)` | an **async generator**: yields `0, 1, …, count - 1`, sleeping `interval` seconds before each value |
| `crawl(start, get_links, *, workers=3, max_pages=50)` | a breadth-first crawler. `await get_links(url)` returns the links found on a page. Visit every reachable page **once**, using an `asyncio.Queue` and `workers` worker tasks, and visit at most `max_pages` pages. Returns the **set** of visited pages. A page whose `get_links` raises still counts as visited, its links are just unknown |

## Examples

```python
>>> async def fake_fetch(url):
...     await asyncio.sleep(0.1)
...     return url.upper()
>>> asyncio.run(fetch_all(["a", "b", "c"], fake_fetch, limit=2))      # 0.2 s: two rounds
{'a': 'A', 'b': 'B', 'c': 'C'}

>>> async def slow(value, seconds):
...     await asyncio.sleep(seconds)
...     return value
>>> asyncio.run(first_completed(slow("tortoise", 1), slow("hare", 0.1)))
'hare'

>>> async def collect():
...     return [tick async for tick in ticker(3, 0.01)]
>>> asyncio.run(collect())
[0, 1, 2]

>>> SITE = {"/": ["/a", "/b"], "/a": ["/b", "/c"], "/b": ["/"], "/c": []}
>>> async def get_links(url):
...     await asyncio.sleep(0.01)
...     return SITE[url]
>>> sorted(asyncio.run(crawl("/", get_links)))
['/', '/a', '/b', '/c']
```

## Hints

<details>
<summary>Hint 1: fetch_all and retry</summary>

Write a small inner `async def one(url)` that does `async with sem:` and returns `await fetch(url)`, then
`results = await asyncio.gather(*(one(u) for u in urls), return_exceptions=True)` and `zip` the URLs with
the results. In `retry`, loop over `range(attempts)`, `return await func(*args)` inside `try`, and
`await asyncio.sleep(delay * 2 ** attempt)` only if another attempt follows.
</details>

<details>
<summary>Hint 2: first_completed</summary>

Wrap each coroutine in a task with `asyncio.create_task`. `done, pending = await asyncio.wait(tasks,
timeout=timeout, return_when=asyncio.FIRST_COMPLETED)` returns two sets. Cancel everything in `pending`.
If `done` is empty, it was a timeout. Otherwise `next(iter(done)).result()` returns the value or
re-raises the exception.
</details>

<details>
<summary>Hint 3: crawl</summary>

Keep a set `seen` of URLs that were **queued** (not just visited), so a page linked from many places is
queued once. Each worker loops: `url = await queue.get()`, visit it, `queue.put_nowait(link)` for every
new link while `len(seen) < max_pages`, then `queue.task_done()` in a `finally`. The main coroutine puts
`start`, starts the workers, `await queue.join()`, and cancels the workers. Because there is only one
thread and no `await` between checking and adding to `seen`, no lock is needed.
</details>

## Check your work

```bash
pytest advanced/11-asyncio/assignments/12-async-crawler -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/11-asyncio/assignments/12-async-crawler/exercise.py),
then tick off assignment 12 in the [progress checklist](../../../../README.md#progress-checklist).
