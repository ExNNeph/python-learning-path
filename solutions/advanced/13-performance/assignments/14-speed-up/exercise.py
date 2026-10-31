"""Assignment 14 · Speed-up: template solution.

Each function keeps its exact results; the comment says what made the old version slow.
"""

import cProfile
import math
import pstats
from collections import Counter, deque


def common_items(a, b):
    # Was O(n·m): `x in b` and `x not in result` searched lists. Sets do both in O(1).
    return sorted(set(a) & set(b))


def rolling_sums(values, k):
    # Was O(n·k): every window was summed from scratch. Slide instead: add the new value,
    # subtract the one that left the window.
    if k > len(values):
        return []
    window = sum(values[:k])
    sums = [window]
    for i in range(k, len(values)):
        window += values[i] - values[i - k]
        sums.append(window)
    return sums


def run_jobs(jobs):
    # Was O(n²): list.pop(0) shifts the whole list every time. deque.popleft() is O(1).
    queue = deque(jobs)
    done = []
    while queue:
        job = queue.popleft()
        if job > 0 and job % 7 == 0:
            queue.append(job // 7)
        done.append(job)
    return done


def count_pairs(numbers, target):
    # Was O(n²): every pair was tested. Instead, for each number count how many earlier
    # numbers were its complement: one pass with a Counter.
    seen = Counter()
    count = 0
    for number in numbers:
        count += seen[target - number]
        seen[number] += 1
    return count


def grid_paths(rows, cols):
    # Was exponential: the recursion recomputed the same sub-grids millions of times.
    # A path is (rows-1) downs and (cols-1) rights in some order: a binomial coefficient.
    # (@functools.cache on the recursive version works too, in O(rows·cols).)
    return math.comb(rows + cols - 2, rows - 1)


def sum_of_squares(n):
    # Was O(n) memory: the list of all squares existed at once. A generator needs O(1).
    return sum(i * i for i in range(n))


def hottest_function(func, *args):
    profiler = cProfile.Profile()
    profiler.runcall(func, *args)
    # stats maps (filename, line, function name) → (primitive calls, calls, tottime, cumtime, callers)
    stats = pstats.Stats(profiler).stats
    (_, _, name), _ = max(stats.items(), key=lambda entry: entry[1][2])
    return name


if __name__ == "__main__":
    import random
    import time

    rng = random.Random(1)
    a = [rng.randrange(100_000) for _ in range(20_000)]
    b = [rng.randrange(100_000) for _ in range(20_000)]
    start = time.perf_counter()
    common_items(a, b)
    print(f"common_items: {time.perf_counter() - start:.2f} s")
