"""Tests for assignment 12. Run: pytest advanced/11-asyncio/assignments/12-async-crawler -v"""

import asyncio
import inspect
import time

import pytest


def run(coro):
    return asyncio.run(coro)


class Tracker:
    """A fake network: records how many calls run at the same time."""

    def __init__(self, delay=0.1, fail=()):
        self.delay, self.fail = delay, set(fail)
        self.active = self.peak = 0
        self.calls = []

    async def fetch(self, url):
        self.calls.append(url)
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(self.delay)
            if url in self.fail:
                raise ConnectionError(url)
            return url.upper()
        finally:
            self.active -= 1


# --- fetch_all -------------------------------------------------------------------

def test_fetch_all(ex):
    net = Tracker(fail={"bad"})
    result = run(ex.fetch_all(["c", "bad", "a"], net.fetch))
    assert list(result) == ["c", "bad", "a"]
    assert result["c"] == "C" and result["a"] == "A"
    assert isinstance(result["bad"], ConnectionError)


def test_fetch_all_is_concurrent(ex):
    net = Tracker(delay=0.2)
    start = time.perf_counter()
    run(ex.fetch_all([str(n) for n in range(5)], net.fetch))
    assert time.perf_counter() - start < 0.5          # sequential: 1.0 s
    assert net.peak == 5


def test_fetch_all_respects_limit(ex):
    net = Tracker(delay=0.05)
    run(ex.fetch_all([str(n) for n in range(10)], net.fetch, limit=3))
    assert net.peak == 3
    assert sorted(net.calls) == sorted(str(n) for n in range(10))


def test_fetch_all_empty(ex):
    assert run(ex.fetch_all([], Tracker().fetch)) == {}


# --- first_completed ---------------------------------------------------------------

async def slow(value, seconds, log=None):
    try:
        await asyncio.sleep(seconds)
        return value
    except asyncio.CancelledError:
        if log is not None:
            log.append(value)
        raise


async def failing(seconds):
    await asyncio.sleep(seconds)
    raise ValueError("failed first")


def test_first_completed_returns_the_fastest(ex):
    start = time.perf_counter()
    assert run(ex.first_completed(slow("tortoise", 1), slow("hare", 0.05))) == "hare"
    assert time.perf_counter() - start < 0.5


def test_first_completed_cancels_the_rest(ex):
    cancelled = []

    async def scenario():
        result = await ex.first_completed(slow("a", 1, cancelled), slow("b", 0.05, cancelled), slow("c", 2, cancelled))
        await asyncio.sleep(0)              # let the cancellations be delivered
        return result

    assert run(scenario()) == "b"
    assert sorted(cancelled) == ["a", "c"]


def test_first_completed_reraises(ex):
    with pytest.raises(ValueError, match="failed first"):
        run(ex.first_completed(slow("late", 1), failing(0.05)))


def test_first_completed_timeout(ex):
    cancelled = []

    async def scenario():
        try:
            await ex.first_completed(slow("x", 1, cancelled), timeout=0.05)
        finally:
            await asyncio.sleep(0)

    start = time.perf_counter()
    with pytest.raises(TimeoutError):
        run(scenario())
    assert time.perf_counter() - start < 0.5
    assert cancelled == ["x"]


# --- retry -------------------------------------------------------------------------

def make_flaky(failures):
    attempts = []

    async def flaky(value):
        attempts.append(time.perf_counter())
        await asyncio.sleep(0)
        if len(attempts) <= failures:
            raise ConnectionError(f"attempt {len(attempts)}")
        return value

    return flaky, attempts


def test_retry_succeeds(ex):
    flaky, attempts = make_flaky(2)
    assert run(ex.retry(flaky, "ok", attempts=3, delay=0.01)) == "ok"
    assert len(attempts) == 3


def test_retry_gives_up(ex):
    flaky, attempts = make_flaky(10)
    with pytest.raises(ConnectionError, match="attempt 4"):
        run(ex.retry(flaky, "x", attempts=4, delay=0.001))
    assert len(attempts) == 4


def test_retry_backs_off_exponentially(ex):
    flaky, attempts = make_flaky(3)
    run(ex.retry(flaky, "ok", attempts=4, delay=0.05))
    gaps = [b - a for a, b in zip(attempts, attempts[1:])]
    # generous bounds: on Windows, asyncio timers may fire up to ~16 ms early
    assert gaps[0] >= 0.03 and gaps[1] >= 0.08 and gaps[2] >= 0.18
    assert gaps[2] < 0.6


def test_retry_no_sleep_after_last_attempt(ex):
    flaky, _ = make_flaky(10)
    start = time.perf_counter()
    with pytest.raises(ConnectionError):
        run(ex.retry(flaky, "x", attempts=1, delay=1))
    assert time.perf_counter() - start < 0.5


# --- ticker -------------------------------------------------------------------------

def test_ticker(ex):
    async def collect():
        return [tick async for tick in ex.ticker(3, 0.01)]

    assert run(collect()) == [0, 1, 2]
    assert inspect.isasyncgenfunction(ex.ticker)


def test_ticker_sleeps_before_each_value(ex):
    async def first():
        async for tick in ex.ticker(5, 0.1):
            return tick

    start = time.perf_counter()
    assert run(first()) == 0
    assert 0.07 <= time.perf_counter() - start < 0.4


# --- crawl -------------------------------------------------------------------------------

SITE = {
    "/": ["/blog", "/about", "/blog"],
    "/blog": ["/blog/1", "/blog/2", "/"],
    "/blog/1": ["/about", "/missing"],
    "/blog/2": ["/blog/1"],
    "/about": [],
}


class FakeSite:
    def __init__(self, pages, delay=0.05):
        self.pages, self.delay = pages, delay
        self.visits = []
        self.active = self.peak = 0

    async def get_links(self, url):
        self.visits.append(url)
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(self.delay)
            if url not in self.pages:
                raise LookupError(url)
            return self.pages[url]
        finally:
            self.active -= 1


def test_crawl_visits_everything_once(ex):
    site = FakeSite(SITE)
    visited = run(ex.crawl("/", site.get_links))
    assert visited == {"/", "/blog", "/about", "/blog/1", "/blog/2", "/missing"}
    assert sorted(site.visits) == sorted(visited)          # no page twice


def test_crawl_uses_workers_concurrently(ex):
    wide = {"/": [f"/p{n}" for n in range(9)], **{f"/p{n}": [] for n in range(9)}}
    site = FakeSite(wide, delay=0.1)
    start = time.perf_counter()
    assert len(run(ex.crawl("/", site.get_links, workers=3))) == 10
    assert site.peak == 3
    assert time.perf_counter() - start < 0.9              # 1 + 9 pages, 3 at a time ≈ 0.4 s


def test_crawl_max_pages(ex):
    chain = {f"/{n}": [f"/{n + 1}"] for n in range(100)}
    site = FakeSite(chain, delay=0)
    visited = run(ex.crawl("/0", site.get_links, max_pages=10))
    assert visited == {f"/{n}" for n in range(10)}
    assert len(site.visits) == 10


def test_crawl_single_page(ex):
    assert run(ex.crawl("/only", FakeSite({"/only": []}).get_links)) == {"/only"}


def test_crawl_broken_start(ex):
    assert run(ex.crawl("/gone", FakeSite({}).get_links)) == {"/gone"}
