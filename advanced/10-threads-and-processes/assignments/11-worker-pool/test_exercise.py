"""Tests for assignment 11. Run: pytest advanced/10-threads-and-processes/assignments/11-worker-pool -v"""

import math
import sys
import threading
import time

import pytest


@pytest.fixture
def tiny_switch_interval():
    """Make threads switch very often, so missing locks show up."""
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    yield
    sys.setswitchinterval(old)


def run_threads(target, count):
    threads = [threading.Thread(target=target) for _ in range(count)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# --- SafeCounter -------------------------------------------------------------

def test_counter_basics(ex):
    counter = ex.SafeCounter()
    assert counter.value == 0
    counter.increment()
    counter.increment(5)
    assert counter.value == 6


def test_counter_value_is_a_property(ex):
    assert isinstance(vars(ex.SafeCounter)["value"], property)


def test_counter_many_threads(ex, tiny_switch_interval):
    counter = ex.SafeCounter()
    run_threads(lambda: [counter.increment() for _ in range(5000)], 8)
    assert counter.value == 40_000


def test_counter_uses_its_lock(ex):
    class SpyLock:
        def __init__(self):
            self.real = threading.Lock()
            self.entered = 0

        def __enter__(self):
            self.real.acquire()
            self.entered += 1
            return self

        def __exit__(self, *exc):
            self.real.release()

    counter = ex.SafeCounter()
    assert isinstance(counter.lock, type(threading.Lock()))
    counter.lock = SpyLock()
    for _ in range(3):
        counter.increment(2)
    assert counter.lock.entered == 3
    assert counter.value == 6


# --- fetch_all ---------------------------------------------------------------

def slow_fetch(url):
    time.sleep(0.3)
    if "bad" in url:
        raise ConnectionError(url)
    return len(url)


def test_fetch_all_results_in_order(ex):
    urls = ["c.net", "a.com", "bad.org", "long-name.io"]
    result = ex.fetch_all(urls, slow_fetch)
    assert list(result) == urls
    assert result["c.net"] == 5 and result["long-name.io"] == 12
    assert isinstance(result["bad.org"], ConnectionError)
    assert result["bad.org"].args == ("bad.org",)


def test_fetch_all_is_concurrent(ex):
    start = time.perf_counter()
    ex.fetch_all([f"site{n}.com" for n in range(8)], slow_fetch)
    assert time.perf_counter() - start < 1.2      # sequential would be 2.4 s


def test_fetch_all_respects_max_workers(ex):
    active, peak, lock = [0], [0], threading.Lock()

    def fetch(url):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        time.sleep(0.05)
        with lock:
            active[0] -= 1
        return url

    ex.fetch_all([str(n) for n in range(10)], fetch, max_workers=3)
    assert peak[0] <= 3


def test_fetch_all_empty(ex):
    assert ex.fetch_all([], slow_fetch) == {}


# --- run_with_timeout ----------------------------------------------------------

def test_run_with_timeout_returns_result(ex):
    assert ex.run_with_timeout(pow, 2, 10, timeout=1) == 1024


def test_run_with_timeout_raises_quickly(ex):
    start = time.perf_counter()
    with pytest.raises(TimeoutError, match="^sleep did not finish within 0.1 s$"):
        ex.run_with_timeout(time.sleep, 1.0, timeout=0.1)
    assert time.perf_counter() - start < 0.6


def test_run_with_timeout_propagates_errors(ex):
    with pytest.raises(ValueError):
        ex.run_with_timeout(int, "x", timeout=1)


# --- process_queue -------------------------------------------------------------

def test_process_queue_order(ex):
    assert ex.process_queue([3, 1, 2], lambda n: n * 10, num_workers=2) == [30, 10, 20]


def test_process_queue_errors_become_values(ex):
    result = ex.process_queue(["1", "x", "3"], int)
    assert result[0] == 1 and result[2] == 3
    assert isinstance(result[1], ValueError)


def test_process_queue_uses_worker_threads(ex):
    names = set()
    lock = threading.Lock()

    def work(n):
        with lock:
            names.add(threading.current_thread().name)
        time.sleep(0.1)
        return n

    start = time.perf_counter()
    assert ex.process_queue(list(range(8)), work, num_workers=4) == list(range(8))
    assert time.perf_counter() - start < 0.6           # 8 jobs × 0.1 s on 4 threads ≈ 0.2 s
    assert threading.main_thread().name not in names
    assert 2 <= len(names) <= 4


def test_process_queue_stops_its_threads(ex):
    before = threading.active_count()
    ex.process_queue(list(range(5)), abs, num_workers=3)
    assert threading.active_count() == before


def test_process_queue_does_not_use_executors(ex):
    import inspect
    assert ex.process_queue([-1], abs) == [1]
    source = inspect.getsource(ex.process_queue)
    assert "Executor" not in source and "Queue" in source


def test_process_queue_empty(ex):
    assert ex.process_queue([], abs) == []


# --- parallel_map ----------------------------------------------------------------

def test_parallel_map(ex):
    assert ex.parallel_map(math.factorial, range(6)) == [1, 1, 2, 6, 24, 120]


def test_parallel_map_other_function(ex):
    assert ex.parallel_map(str.upper, ["a", "b"], workers=1) == ["A", "B"]
