"""Assignment 14 · Speed-up.

Every function in this file is CORRECT but SLOW. Make each one fast without changing what it returns.
The tests check the results on small inputs (they already pass) and the speed on large ones (they fail).
Check your work:  pytest advanced/13-performance/assignments/14-speed-up -v
"""

import cProfile
import pstats
from collections import Counter, deque


def common_items(a, b):
    """The sorted list of distinct items that appear in both a and b."""
    result = []
    for x in a:
        if x in b and x not in result:
            result.append(x)
    return sorted(result)


def rolling_sums(values, k):
    """The sums of all windows of k consecutive values: [sum(values[0:k]), sum(values[1:k+1]), ...]."""
    return [sum(values[i:i + k]) for i in range(len(values) - k + 1)]


def run_jobs(jobs):
    """Process jobs first-in, first-out. A job divisible by 7 (and > 0) adds job // 7 to the END of
    the queue. Return the jobs in the order they were processed."""
    queue = list(jobs)
    done = []
    while queue:
        job = queue.pop(0)
        if job > 0 and job % 7 == 0:
            queue.append(job // 7)
        done.append(job)
    return done


def count_pairs(numbers, target):
    """How many index pairs i < j have numbers[i] + numbers[j] == target."""
    count = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                count += 1
    return count


def grid_paths(rows, cols):
    """The number of paths from the top-left to the bottom-right cell of a rows × cols grid,
    moving only right or down."""
    if rows == 1 or cols == 1:
        return 1
    return grid_paths(rows - 1, cols) + grid_paths(rows, cols - 1)


def sum_of_squares(n):
    """0² + 1² + ... + (n-1)². Correct and fast enough, but it uses far too much MEMORY."""
    return sum([i * i for i in range(n)])


def hottest_function(func, *args):
    """Run func(*args) under cProfile and return the NAME of the function with the highest
    tottime (time spent in the function itself). TODO: write this one from scratch."""
    raise NotImplementedError


if __name__ == "__main__":
    import random
    import time

    rng = random.Random(1)
    a = [rng.randrange(100_000) for _ in range(20_000)]
    b = [rng.randrange(100_000) for _ in range(20_000)]
    start = time.perf_counter()
    common_items(a, b)
    print(f"common_items: {time.perf_counter() - start:.2f} s")
