"""Assignment 03 · Vector.

Replace each `raise NotImplementedError` with your code. Add the special methods listed in the README:
__repr__, __str__, __format__, __len__, __getitem__, __iter__, __eq__, __hash__, __add__, __sub__,
__mul__, __rmul__, __truediv__, __matmul__, __neg__, __abs__ and __bool__.
Check your work:  pytest advanced/03-the-data-model/assignments/03-vector -v
"""

import math


class Vector:
    """An immutable n-dimensional vector: Vector(3, 4)."""

    def __init__(self, *components):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


if __name__ == "__main__":
    v, w = Vector(3, 4), Vector(1, 2)
    print(f"{v!r} + {w!r} = {v + w!r}")
    print(f"|v| = {abs(v)}, v·w = {v @ w}, v/3 = {v / 3:.3f}")
