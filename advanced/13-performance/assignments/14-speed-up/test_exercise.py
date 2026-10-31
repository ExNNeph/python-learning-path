"""Tests for assignment 14. Run: pytest advanced/13-performance/assignments/14-speed-up -v

The `correct_*` tests use small inputs and pass with the slow starter code: they protect the results
while you optimise. The `fast_*` tests use large inputs and a time limit that is about 10 times
higher than a good solution needs; the slow versions take seconds (and a few minutes in total).
"""

import random
import time
import tracemalloc

import pytest

LIMIT = 0.5          # seconds


def timed(func, *args):
    start = time.perf_counter()
    result = func(*args)
    return result, time.perf_counter() - start


@pytest.fixture
def rng():
    return random.Random(2026)


# --- common_items ------------------------------------------------------------------

def test_correct_common_items(ex):
    assert ex.common_items([3, 1, 2, 3, 5], [5, 3, 3, 9]) == [3, 5]
    assert ex.common_items([], [1]) == []
    assert ex.common_items(["b", "a"], ("a", "b", "c")) == ["a", "b"]


def test_fast_common_items(ex, rng):
    a = [rng.randrange(100_000) for _ in range(20_000)]
    b = [rng.randrange(100_000) for _ in range(20_000)]
    result, seconds = timed(ex.common_items, a, b)
    assert result == sorted(set(a) & set(b))
    assert seconds < LIMIT, f"took {seconds:.2f} s"


# --- rolling_sums --------------------------------------------------------------------

def test_correct_rolling_sums(ex):
    assert ex.rolling_sums([1, 2, 3, 4, 5], 2) == [3, 5, 7, 9]
    assert ex.rolling_sums([1, 2, 3], 3) == [6]
    assert ex.rolling_sums([1, 2, 3], 1) == [1, 2, 3]
    assert ex.rolling_sums([1, 2], 3) == []
    assert ex.rolling_sums([5, -5, 5, -5], 2) == [0, 0, 0]


def test_fast_rolling_sums(ex):
    values = list(range(200_000))
    result, seconds = timed(ex.rolling_sums, values, 2000)
    assert len(result) == 198_001
    assert result[0] == sum(range(2000)) and result[-1] == sum(range(198_000, 200_000))
    assert seconds < LIMIT, f"took {seconds:.2f} s"


# --- run_jobs -------------------------------------------------------------------------

def test_correct_run_jobs(ex):
    assert ex.run_jobs([49, 3, 14]) == [49, 3, 14, 7, 2, 1]
    assert ex.run_jobs([]) == []
    assert ex.run_jobs([0, 7]) == [0, 7, 1]


def test_fast_run_jobs(ex):
    result, seconds = timed(ex.run_jobs, range(140_000))
    assert result[:3] == [0, 1, 2] and len(result) == 163_331
    assert seconds < LIMIT, f"took {seconds:.2f} s"


# --- count_pairs ---------------------------------------------------------------------------

def test_correct_count_pairs(ex):
    assert ex.count_pairs([1, 5, 3, 3, 7], 6) == 2
    assert ex.count_pairs([2, 2, 2], 4) == 3
    assert ex.count_pairs([1, 2], 10) == 0
    assert ex.count_pairs([], 0) == 0
    assert ex.count_pairs([3], 6) == 0


def test_fast_count_pairs(ex, rng):
    numbers = [rng.randrange(1000) for _ in range(12_000)]
    result, seconds = timed(ex.count_pairs, numbers, 1000)
    counts = [0] * 1000
    for n in numbers:
        counts[n] += 1
    expected = sum(counts[x] * counts[1000 - x] for x in range(1, 500)) + counts[500] * (counts[500] - 1) // 2
    assert result == expected
    assert seconds < LIMIT, f"took {seconds:.2f} s"


# --- grid_paths --------------------------------------------------------------------------------

@pytest.mark.parametrize("rows, cols, expected", [(1, 1, 1), (1, 5, 1), (2, 2, 2), (3, 3, 6), (3, 4, 10), (5, 2, 5)])
def test_correct_grid_paths(ex, rows, cols, expected):
    assert ex.grid_paths(rows, cols) == expected


def test_fast_grid_paths(ex):
    result, seconds = timed(ex.grid_paths, 15, 15)
    assert result == 40_116_600
    assert seconds < LIMIT, f"took {seconds:.2f} s"
    assert ex.grid_paths(60, 40) == 3_332_420_398_982_499_757_882_998_720


# --- sum_of_squares ------------------------------------------------------------------------------

def test_correct_sum_of_squares(ex):
    assert ex.sum_of_squares(0) == 0
    assert ex.sum_of_squares(4) == 14


def test_lean_sum_of_squares(ex):
    tracemalloc.start()
    try:
        result = ex.sum_of_squares(1_000_000)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert result == 333_332_833_333_500_000
    assert peak < 1_000_000, f"peak memory {peak / 1e6:.1f} MB"


# --- hottest_function ------------------------------------------------------------------------------

def busy_loop(n):
    total = 0
    for i in range(n):
        total += i * i
    return total


def quick(n):
    return n + 1


def program():
    for _ in range(3):
        quick(1)
    busy_loop(300_000)
    return "done"


def test_hottest_function(ex):
    assert ex.hottest_function(program) == "busy_loop"


def test_hottest_function_passes_arguments(ex):
    def outer(a, b):
        return busy_loop(a) + quick(b)

    assert ex.hottest_function(outer, 200_000, 1) == "busy_loop"
