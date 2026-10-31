"""Assignment 11 · Worker pool.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/10-threads-and-processes/assignments/11-worker-pool -v
"""

import concurrent.futures
import queue
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


class SafeCounter:
    """A counter that many threads may increment at the same time."""

    def __init__(self):
        raise NotImplementedError

    def increment(self, amount=1):
        raise NotImplementedError

    @property
    def value(self):
        raise NotImplementedError


def fetch_all(urls, fetch, *, max_workers=8):
    """Call fetch(url) concurrently; return {url: result or exception} in input order."""
    raise NotImplementedError


def run_with_timeout(func, *args, timeout):
    """Return func(*args), or raise TimeoutError after `timeout` seconds without waiting longer."""
    raise NotImplementedError


def process_queue(items, worker, *, num_workers=4):
    """Process items with num_workers threads fed by a queue.Queue; results in input order."""
    raise NotImplementedError


def parallel_map(func, items, *, workers=2):
    """list(map(func, items)), computed in a ProcessPoolExecutor."""
    raise NotImplementedError


if __name__ == "__main__":
    import math
    import time

    start = time.perf_counter()
    print(fetch_all(["a.com", "b.org", "c.net"], lambda url: (time.sleep(0.5), len(url))[1]))
    print(f"fetched in {time.perf_counter() - start:.1f} s")
    print(parallel_map(math.factorial, range(10)))
