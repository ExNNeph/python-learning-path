# Assignment 08 · Typed cache

> **Lesson:** [07 · Protocols and generics](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Write a small library whose types are as precise as those of the standard library: a **generic** LRU
cache, a protocol, a function with a **bounded** type variable, a decorator factory typed with
**`ParamSpec`**, and an **overloaded** function. The tests check the behaviour, run `mypy --strict` on
your file, **and** type-check a piece of code that uses your library, to make sure mypy infers the
right types for your users.

## What to write

| Name | Specification |
|---|---|
| `LRUCache[K, V]` | `LRUCache(capacity)` (below 1: `ValueError`). `get(key) -> V \| None` returns the value and marks the key as **recently used**. `put(key, value)` stores it (also marking it as recently used); when the cache is full, the **least recently used** entry is removed first. `len(cache)`, `key in cache` (does **not** count as a use) and `items() -> list[tuple[K, V]]` (least recently used first) |
| `HasArea` | a `Protocol` with a method `area(self) -> float` |
| `total_area(shapes)` | the sum of `area()` over any iterable of `HasArea` objects |
| `largest(items)` | the largest item of any iterable of comparable items, typed with a `TypeVar` bound to a protocol with `__lt__`, so that `largest([3, 1])` is an `int` for mypy. Empty: `ValueError` |
| `logged(log)` | a decorator **factory**: `@logged(entries)` appends `"add(1, b=2) -> 3"` to the list `entries` on every call (positional arguments with `repr`, then keyword arguments as `name=repr`). The decorated function keeps its exact signature for mypy (`ParamSpec`) and its name (`functools.wraps`) |
| `convert(text, kind)` | `kind="int"` returns `int(text)`, `kind="float"` returns `float(text)`. Two `@overload`s with `Literal["int"]` and `Literal["float"]` make mypy see `int` or `float` |

The whole file must pass `mypy --strict`, without `Any` in the public signatures (inside the
implementation of the overloaded function, `Any` or a union is fine).

## Examples

```python
>>> cache: LRUCache[str, int] = LRUCache(2)
>>> cache.put("a", 1)
>>> cache.put("b", 2)
>>> cache.get("a")        # "a" is now the most recently used
1
>>> cache.put("c", 3)     # full: evicts "b", the least recently used
>>> cache.items()
[('a', 1), ('c', 3)]
>>> "b" in cache, cache.get("b")
(False, None)

>>> largest(["pear", "fig", "plum"])
'plum'

>>> entries: list[str] = []
>>> @logged(entries)
... def add(a: int, b: int = 0) -> int:
...     return a + b
>>> add(1, b=2)
3
>>> entries
['add(1, b=2) -> 3']

>>> convert("2.5", "float")
2.5
```

## Hints

<details>
<summary>Hint 1: LRUCache</summary>

`K = TypeVar("K")`, `V = TypeVar("V")`, `class LRUCache(Generic[K, V])`. A
`collections.OrderedDict[K, V]` keeps the order for you: `move_to_end(key)` marks a key as recently used,
`popitem(last=False)` removes the oldest. Annotate the attribute: `self._data: OrderedDict[K, V] = OrderedDict()`.
</details>

<details>
<summary>Hint 2: largest and logged</summary>

`class SupportsLessThan(Protocol): def __lt__(self, other: Any, /) -> bool: ...` and
`C = TypeVar("C", bound=SupportsLessThan)`. `max()` with an empty iterable raises `ValueError` already.

`logged(log: list[str]) -> Callable[[Callable[P, R]], Callable[P, R]]`: the factory returns the decorator,
the decorator returns the wrapper, and the wrapper has `*args: P.args, **kwargs: P.kwargs`.
</details>

<details>
<summary>Hint 3: convert</summary>

```python
@overload
def convert(text: str, kind: Literal["int"]) -> int: ...
@overload
def convert(text: str, kind: Literal["float"]) -> float: ...
def convert(text: str, kind: str) -> int | float:
    ...
```
</details>

## Check your work

```bash
pytest advanced/07-protocols-and-generics/assignments/08-typed-cache -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/07-protocols-and-generics/assignments/08-typed-cache/exercise.py),
then tick off assignment 08 in the [progress checklist](../../../../README.md#progress-checklist).
