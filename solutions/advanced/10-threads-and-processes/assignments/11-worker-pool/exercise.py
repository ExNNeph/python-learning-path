"""Assignment 11 · Worker pool: template solution."""

import concurrent.futures
import queue
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


class SafeCounter:
    def __init__(self):
        self.lock = threading.Lock()
        self._value = 0

    def increment(self, amount=1):
        with self.lock:                  # read + add + write must be one indivisible step
            self._value += amount

    @property
    def value(self):
        return self._value               # a single read needs no lock


def fetch_all(urls, fetch, *, max_workers=8):
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        # Submit everything first, so all calls run concurrently; then collect in input order.
        futures = {url: pool.submit(fetch, url) for url in urls}
    # Leaving the with block waited for all futures. An error stays inside its own future.
    return {url: future.exception() or future.result() for url, future in futures.items()}


def run_with_timeout(func, *args, timeout):
    pool = ThreadPoolExecutor(max_workers=1)
    try:
        return pool.submit(func, *args).result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        # On 3.10 this is not the built-in TimeoutError; raise the built-in one for every version.
        raise TimeoutError(f"{func.__name__} did not finish within {timeout} s") from None
    finally:
        # No `with`: its exit would wait for func. The thread keeps running in the background;
        # Python cannot kill a thread, it can only stop waiting for it.
        pool.shutdown(wait=False)


_STOP = object()                         # sentinel: "no more work"


def process_queue(items, worker, *, num_workers=4):
    jobs = queue.Queue()
    results = [None] * len(items)

    def run():
        while True:
            job = jobs.get()
            if job is _STOP:
                return
            index, item = job
            try:
                results[index] = worker(item)   # each index is written by exactly one thread
            except Exception as error:
                results[index] = error

    threads = [threading.Thread(target=run) for _ in range(num_workers)]
    for thread in threads:
        thread.start()
    for job in enumerate(items):
        jobs.put(job)
    for _ in threads:
        jobs.put(_STOP)                  # one per worker, after all the real jobs
    for thread in threads:
        thread.join()
    return results


def parallel_map(func, items, *, workers=2):
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(func, items))


if __name__ == "__main__":
    import math
    import time

    start = time.perf_counter()
    print(fetch_all(["a.com", "b.org", "c.net"], lambda url: (time.sleep(0.5), len(url))[1]))
    print(f"fetched in {time.perf_counter() - start:.1f} s")
    print(parallel_map(math.factorial, range(10)))
