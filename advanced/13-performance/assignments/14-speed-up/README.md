# Assignment 14 · Speed-up

> **Lesson:** [13 · Performance](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2 h

## Goal

This assignment is the other way round: the starter file already **works**. Every function returns the
right result, and the `correct_*` tests already pass. But each one is slow (or, in one case, hungry for
memory), and the `fast_*` tests fail. Find out **why** each one is slow, fix the cause, and keep the
results exactly the same. Then write a small helper that finds hotspots with `cProfile`.

## What to do

| Function | Returns | Hint at the problem |
|---|---|---|
| `common_items(a, b)` | the sorted distinct items in both | membership tests on lists |
| `rolling_sums(values, k)` | the sum of every window of `k` values | every window is summed from scratch |
| `run_jobs(jobs)` | the jobs in FIFO processing order | the queue is a list, emptied from the front |
| `count_pairs(numbers, target)` | the number of pairs `i < j` with `numbers[i] + numbers[j] == target` | every pair is tested |
| `grid_paths(rows, cols)` | the number of right/down paths through a grid | the same sub-problems are solved again and again |
| `sum_of_squares(n)` | `0² + 1² + … + (n-1)²` | fast enough, but needs ~40 MB of memory for `n = 1 000 000` |
| `hottest_function(func, *args)` | **new:** run `func(*args)` under `cProfile` and return the **name** of the function with the highest `tottime` | |

Rules:

- Do not change what a function returns, including for edge cases like empty input or `k > len(values)`.
- The speed tests allow 0.5 s for an input where a good solution needs a few hundredths of a second.
- `sum_of_squares(1_000_000)` must stay below 1 MB of peak memory (measured with `tracemalloc`).

## Workflow

1. Run the tests and read which ones fail. The slow versions take a few seconds each.
2. Measure before you change anything, for example:
   ```bash
   python -m timeit -s "import exercise as e; a = list(range(5000))" "e.common_items(a, a)"
   ```
   (from inside this folder)
3. Change one function, run its `correct_` **and** `fast_` tests, measure again.

## Hints

<details>
<summary>Hint 1: the data-structure fixes</summary>

`common_items`: what is the intersection of two **sets**? `run_jobs`: `collections.deque` has an O(1)
`popleft()`. `sum_of_squares`: remove two characters, `[` and `]`, and think about why that helps.
</details>

<details>
<summary>Hint 2: the algorithm fixes</summary>

`rolling_sums`: the next window's sum is the previous sum, plus the value that enters, minus the value
that leaves. `count_pairs`: walk through the numbers once; for each number, how many **earlier** numbers
would complete it to `target`? A `Counter` of the numbers seen so far answers that in O(1).
`grid_paths`: `@functools.cache` on the recursive version is enough. (Or count combinatorially: every
path is a sequence of `rows - 1` downs and `cols - 1` rights.)
</details>

<details>
<summary>Hint 3: hottest_function</summary>

`profiler = cProfile.Profile()`, `profiler.runcall(func, *args)`. `pstats.Stats(profiler).stats` is a
dict: the key is `(filename, line, function_name)`, the value a tuple whose **third** item (index 2) is
`tottime`. `max(..., key=...)` does the rest.
</details>

## Check your work

```bash
pytest advanced/13-performance/assignments/14-speed-up -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/13-performance/assignments/14-speed-up/exercise.py):
each function has a comment that explains what made the old version slow. Then tick off assignment 14 in
the [progress checklist](../../../../README.md#progress-checklist).
