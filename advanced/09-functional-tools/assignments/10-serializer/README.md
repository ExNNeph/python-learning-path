# Assignment 10 · Serializer

> **Lesson:** [09 · Functional tools](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2 h

## Goal

Build four functional tools: a JSON preparer that is **open for new types** (`singledispatch`), a
version number type that compares correctly (`total_ordering`), function composition (`reduce`), and an
update function for nested data that never changes its input (immutability).

## What to write

### `to_jsonable(value)`

A `singledispatch` function that turns Python values into something `json.dumps` accepts:

| Type | Result |
|---|---|
| `None`, `bool`, `int`, `float`, `str` | unchanged |
| `list`, `tuple` | a list, items converted recursively |
| `dict` (any `Mapping`) | a dict with `str(key)` keys, values converted recursively |
| `set`, `frozenset` | a **sorted** list of the converted items |
| `datetime.date` and `datetime.datetime` | `value.isoformat()` |
| `decimal.Decimal` | `str(value)` (keeps the exact digits) |
| an `Enum` member | its converted `.value` |
| a dataclass instance | a dict of its fields, converted recursively |
| anything else | `TypeError("cannot convert Foo to JSON")` with the type name |

Other code must be able to add types without editing your function: `@to_jsonable.register`.

### `Version(text)`

A version number like `"1.10.2"`, decorated with `@total_ordering`.

| Feature | Specification |
|---|---|
| parsing | dot-separated non-negative integers; anything else (`""`, `"1..2"`, `"1.a"`, `"-1"`): `ValueError` |
| comparing | numerically, part by part: `1.10 > 1.9`. Trailing zeros do not count: `Version("1.2") == Version("1.2.0")` |
| `hash` | consistent with `==` |
| `repr`, `str` | `Version('1.10.2')` and `1.10.2` (the text as given) |
| other types | `==` with a non-`Version` is `False`; `<` with one raises `TypeError` |

### `compose(*funcs)` and `update_in(data, path, func)`

| Function | Specification |
|---|---|
| `compose(*funcs)` | `compose(f, g, h)(x) == f(g(h(x)))`; no functions: the identity. Use `functools.reduce` |
| `update_in(data, path, func)` | returns a **new** nested structure of dicts and lists where the value at `path` (a sequence of keys and indexes) is replaced by `func(old_value)`. The input is **never** changed. Parts that are not on the path are **shared** (the very same objects). A missing key or index raises `KeyError` / `IndexError`. An empty path applies `func` to `data` itself |

## Examples

```python
>>> to_jsonable({"when": date(2026, 10, 31), "tags": {"b", "a"}, "price": Decimal("9.90")})
{'when': '2026-10-31', 'tags': ['a', 'b'], 'price': '9.90'}

>>> sorted(Version(v) for v in ["1.10", "1.9.3", "1.9"])
[Version('1.9'), Version('1.9.3'), Version('1.10')]
>>> Version("2.0") == Version("2"), Version("1.0.1") >= Version("1")
(True, True)

>>> slug = compose("-".join, str.split, str.lower)
>>> slug("Functional Tools Rock")
'functional-tools-rock'

>>> config = {"db": {"ports": [5432, 5433]}, "debug": False}
>>> new = update_in(config, ["db", "ports", 1], lambda p: p + 1)
>>> new
{'db': {'ports': [5432, 5434]}, 'debug': False}
>>> config["db"]["ports"]
[5432, 5433]
```

## Hints

<details>
<summary>Hint 1: to_jsonable</summary>

The base function (the fallback) raises the `TypeError`, **but** first checks
`dataclasses.is_dataclass(value)`: dataclasses have no common base class to register. Register
`collections.abc.Mapping` instead of `dict`, and `(list, tuple)` with two `register` calls or one
implementation registered twice. Register `datetime.date`: `datetime.datetime` is a subclass of it.
</details>

<details>
<summary>Hint 2: Version</summary>

Parse into a tuple of ints, then strip trailing zeros for comparisons: `(1, 2, 0)` → `(1, 2)`. Keep that
"key" tuple in an attribute and use it in `__eq__`, `__lt__` and `__hash__`. `str.isdigit()` rejects
`"-1"` and `""`.
</details>

<details>
<summary>Hint 3: update_in</summary>

Recursion: with an empty path, return `func(data)`. Otherwise take the first key, compute the new child
with `update_in(data[key], rest, func)`, and build a **copy** of `data` with that one entry replaced:
`{**data, key: child}` for dicts, `[*data[:key], child, *data[key + 1:]]` for lists (careful with
negative indexes: `data[key]` first, so a bad index fails early, then normalise it with
`range(len(data))[key]`).
</details>

## Check your work

```bash
pytest advanced/09-functional-tools/assignments/10-serializer -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/09-functional-tools/assignments/10-serializer/exercise.py),
then tick off assignment 10 in the [progress checklist](../../../../README.md#progress-checklist).
