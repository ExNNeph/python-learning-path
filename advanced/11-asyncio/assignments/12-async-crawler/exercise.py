"""Assignment 12 · Async crawler.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/11-asyncio/assignments/12-async-crawler -v
"""

import asyncio


async def fetch_all(urls, fetch, *, limit=5):
    """Await fetch(url) for all urls, at most `limit` at a time; {url: result or exception}."""
    raise NotImplementedError


async def first_completed(*coroutines, timeout=None):
    """Return the result of the first coroutine to finish; cancel the others."""
    raise NotImplementedError


async def retry(func, *args, attempts=3, delay=0.1):
    """Await func(*args) up to `attempts` times, sleeping delay, 2*delay, 4*delay, ... in between."""
    raise NotImplementedError


async def ticker(count, interval):
    """Async generator: yield 0 .. count-1, sleeping `interval` before each value."""
    raise NotImplementedError
    yield  # keeps this an async generator until you write your own yield


async def crawl(start, get_links, *, workers=3, max_pages=50):
    """Visit every page reachable from start once (at most max_pages); return the set of pages."""
    raise NotImplementedError


if __name__ == "__main__":
    SITE = {"/": ["/blog", "/about"], "/blog": ["/blog/1", "/blog/2", "/"], "/blog/1": ["/about"],
            "/blog/2": ["/blog/1"], "/about": []}

    async def get_links(url):
        await asyncio.sleep(0.1)
        return SITE[url]

    print(sorted(asyncio.run(crawl("/", get_links))))
