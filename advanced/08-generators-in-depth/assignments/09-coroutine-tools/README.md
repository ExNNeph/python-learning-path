# Assignment 09 · Coroutine tools

> **Lesson:** [08 · Generators in depth](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Use every generator feature from the lesson: `yield from` for recursion and for return values, `send`
for coroutines that receive data, `throw` to signal a generator, and `close` to shut down a whole push
pipeline.

## What to write

### Delegation and return values

| Function | Specification |
|---|---|
| `flatten(items)` | yields the leaves of arbitrarily nested iterables, depth first: `[1, (2, [3]), {4}]` → `1, 2, 3, 4`. Strings and bytes are leaves, not iterables. Use `yield from` |
| `counted(iterable)` | yields every item and **returns** how many there were |
| `chain_with_counts(*iterables)` | yields the items of all iterables, in order, and **returns** the list of their counts. Use `yield from counted(...)` |

### Coroutines

| Name | Specification |
|---|---|
| `@primed` | a decorator for generator functions: calling the decorated function creates the generator **and** advances it to its first `yield`, so it is ready for `send()` |
| `averager()` | primed. `send(number)` returns the running average of all numbers sent so far |
| `accumulator()` | primed. `send(number)` adds it and returns the total; `send(None)` returns the total unchanged. `throw(Reset)` sets the total back to `0` and returns `0` (the class `Reset` is given) |

### A push pipeline

All four are primed coroutines. Closing one stage must **close the stage(s) it sends to**, so closing
the head of a pipeline shuts down the whole pipeline.

| Name | Specification |
|---|---|
| `collect(results)` | appends every value it receives to the list `results` |
| `grep(pattern, target)` | sends a received line on to `target` only if it contains `pattern` |
| `transform(func, target)` | sends `func(value)` to `target` |
| `broadcast(*targets)` | sends every received value to all targets, in order |

## Examples

```python
>>> list(flatten([1, [2, (3, "four")], [[5]]]))
[1, 2, 3, 'four', 5]

>>> def show():
...     counts = yield from chain_with_counts("ab", [1, 2, 3])
...     print("counts:", counts)
>>> list(show())
counts: [2, 3]
['a', 'b', 1, 2, 3]

>>> avg = averager()            # primed: no next() needed
>>> avg.send(10), avg.send(20)
(10.0, 15.0)

>>> acc = accumulator()
>>> acc.send(5), acc.send(7), acc.throw(Reset), acc.send(1)
(5, 12, 0, 1)

>>> errors, everything = [], []
>>> pipeline = broadcast(grep("ERROR", transform(str.lower, collect(errors))), collect(everything))
>>> for line in ["ERROR disk full", "INFO started", "ERROR timeout"]:
...     pipeline.send(line)
>>> errors
['error disk full', 'error timeout']
>>> len(everything)
3
>>> pipeline.close()            # closes grep, transform and both collects
```

## Hints

<details>
<summary>Hint 1: flatten and counted</summary>

`isinstance(item, (str, bytes))` first: those are leaves. For everything else, `try: iter(item)` tells
you if it is iterable (`TypeError` means it is a leaf). In `counted`, count inside the loop and `return`
after it. In `chain_with_counts`, `count = yield from counted(iterable)`.
</details>

<details>
<summary>Hint 2: primed, averager and accumulator</summary>

`primed` is a normal wrapping decorator: create the generator with `func(*args, **kwargs)`, call
`next()` on it, return it. Use `functools.wraps`.

In `accumulator`, put `value = yield total` inside a `try` and catch `Reset` around it: in the `except`,
set `total = 0`; the loop then yields the new total.
</details>

<details>
<summary>Hint 3: the pipeline stages</summary>

Every stage has the same shape:

```python
@primed
def stage(..., target):
    try:
        while True:
            value = yield
            ...  # maybe target.send(...)
    finally:
        target.close()
```

`collect` has no target, so it needs no `finally`.
</details>

## Check your work

```bash
pytest advanced/08-generators-in-depth/assignments/09-coroutine-tools -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/08-generators-in-depth/assignments/09-coroutine-tools/exercise.py),
then tick off assignment 09 in the [progress checklist](../../../../README.md#progress-checklist).
