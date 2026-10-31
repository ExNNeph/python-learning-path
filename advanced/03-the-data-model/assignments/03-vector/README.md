# Assignment 03 · Vector

> **Lesson:** [03 · The data model](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Write an **immutable n-dimensional vector** that feels like a built-in type: it prints well, compares
and hashes correctly, supports the arithmetic operators in both directions, and works with `len`, `abs`,
indexing, iteration, unpacking and f-string format specs.

## What to write

`Vector(*components)` stores its components (ints or floats) in a **tuple**. At least one component is
required, otherwise `ValueError`.

| Syntax | Result |
|---|---|
| `repr(v)` | `Vector(1, 2.5)` |
| `str(v)` | `(1, 2.5)` |
| `f"{v:.1f}"` | the format spec applied to **each** component: `(1.0, 2.5)`. An empty spec gives `str(v)` |
| `len(v)`, `v[i]`, `v[a:b]`, `for x in v`, `x, y = v` | number of components, a component, **a `Vector`** for slices, iteration, unpacking |
| `v == w` | `True` if `w` is a `Vector` with equal components. Comparing with anything else is `False` (return `NotImplemented`) |
| `hash(v)` | consistent with `==`, so vectors work in sets and as dict keys |
| `v + w`, `v - w` | component-wise. Different lengths: `ValueError`. A non-vector operand: `TypeError` (via `NotImplemented`) |
| `v * k`, `k * v`, `v / k` | scale by an `int` or `float` `k` |
| `v @ w` | the dot product (a number). Different lengths: `ValueError` |
| `-v`, `abs(v)`, `bool(v)` | negation, length (magnitude) as a `float`, `False` only for the zero vector |

## Examples

```python
>>> v, w = Vector(3, 4), Vector(1, 2)
>>> v
Vector(3, 4)
>>> print(v + w, v - w, 2 * v, v / 2)
(4, 6) (2, 2) (6, 8) (1.5, 2.0)
>>> abs(v), v @ w, -w
(5.0, 11, Vector(-1, -2))
>>> f"{w:.2f}"
'(1.00, 2.00)'
>>> Vector(1, 2, 3)[1:]
Vector(2, 3)
>>> x, y = v
>>> {Vector(1, 2), Vector(1, 2)}
{Vector(1, 2)}
>>> v == (3, 4)
False
>>> v + Vector(1, 2, 3)
Traceback (most recent call last):
ValueError: vectors must have the same length
```

## Hints

<details>
<summary>Hint 1: storing and protecting the data</summary>

Store `tuple(components)` in an attribute like `self._components`. Because no method ever changes it,
the vector is immutable and may be hashed: `hash(self._components)`.
</details>

<details>
<summary>Hint 2: one helper for + and -</summary>

A small helper method that checks the other operand (`NotImplemented` if it is not a `Vector`,
`ValueError` for a different length) keeps `__add__`, `__sub__` and `__matmul__` short.
`zip(self, other)` pairs up the components; `Vector(*(a + b for a, b in ...))` builds the result.
</details>

<details>
<summary>Hint 3: scalars and format</summary>

`isinstance(k, (int, float))` tells you if `k` is a scalar; return `NotImplemented` otherwise.
`__rmul__` can simply be `__mul__`. For `__format__(self, spec)`, use the built-in `format(x, spec)`
on each component and join them.
</details>

## Check your work

```bash
pytest advanced/03-the-data-model/assignments/03-vector -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/03-the-data-model/assignments/03-vector/exercise.py),
then tick off assignment 03 in the [progress checklist](../../../../README.md#progress-checklist).
