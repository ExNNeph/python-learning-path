"""Assignment 12 · Async crawler: template solution."""

import asyncio


async def fetch_all(urls, fetch, *, limit=5):
    sem = asyncio.Semaphore(limit)

    async def one(url):
        async with sem:                      # at most `limit` coroutines past this line at once
            return await fetch(url)

    results = await asyncio.gather(*(one(url) for url in urls), return_exceptions=True)
    return dict(zip(urls, results))          # gather keeps the input order


async def first_completed(*coroutines, timeout=None):
    tasks = [asyncio.create_task(coro) for coro in coroutines]
    try:
        done, _ = await asyncio.wait(tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()                # the losers (or everything, on a timeout)
    if not done:
        raise TimeoutError(f"nothing finished within {timeout} s")
    return next(iter(done)).result()         # the value, or the winner's exception re-raised


async def retry(func, *args, attempts=3, delay=0.1):
    for attempt in range(attempts):
        try:
            return await func(*args)
        except Exception:
            if attempt == attempts - 1:
                raise                        # out of attempts: the last error propagates
            await asyncio.sleep(delay * 2 ** attempt)   # exponential backoff: 1x, 2x, 4x, ...


async def ticker(count, interval):
    for i in range(count):
        await asyncio.sleep(interval)
        yield i


async def crawl(start, get_links, *, workers=3, max_pages=50):
    queue = asyncio.Queue()
    seen = {start}                           # queued pages: each page enters the queue once
    visited = set()

    async def worker():
        while True:
            url = await queue.get()
            try:
                visited.add(url)
                try:
                    links = await get_links(url)
                except Exception:
                    links = []               # a broken page is visited, its links are unknown
                for link in links:
                    # No await between the check and the add: no other task can run in between.
                    if link not in seen and len(seen) < max_pages:
                        seen.add(link)
                        queue.put_nowait(link)
            finally:
                queue.task_done()

    queue.put_nowait(start)
    tasks = [asyncio.create_task(worker()) for _ in range(workers)]
    await queue.join()                       # every queued page has been processed
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)   # let the cancellations finish
    return visited


if __name__ == "__main__":
    SITE = {"/": ["/blog", "/about"], "/blog": ["/blog/1", "/blog/2", "/"], "/blog/1": ["/about"],
            "/blog/2": ["/blog/1"], "/about": []}

    async def get_links(url):
        await asyncio.sleep(0.1)
        return SITE[url]

    print(sorted(asyncio.run(crawl("/", get_links))))
