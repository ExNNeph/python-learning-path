"""Assignment 03 · Vector: template solution."""

import math


class Vector:
    """An immutable n-dimensional vector: Vector(3, 4)."""

    def __init__(self, *components):
        if not components:
            raise ValueError("a vector needs at least one component")
        self._components = tuple(components)     # a tuple, and never reassigned: immutable

    # --- text ----------------------------------------------------------------

    def __repr__(self):
        return f"Vector({', '.join(map(repr, self))})"

    def __str__(self):
        return f"({', '.join(map(str, self))})"

    def __format__(self, spec):
        if not spec:
            return str(self)
        return f"({', '.join(format(x, spec) for x in self)})"

    # --- container -----------------------------------------------------------

    def __len__(self):
        return len(self._components)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Vector(*self._components[index])   # slices stay vectors
        return self._components[index]

    def __iter__(self):
        return iter(self._components)

    # --- equality and hashing ------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self._components == other._components

    def __hash__(self):
        return hash(self._components)              # same data as __eq__, so equal → equal hash

    # --- arithmetic ----------------------------------------------------------

    def _check(self, other):
        if not isinstance(other, Vector):
            return False
        if len(self) != len(other):
            raise ValueError("vectors must have the same length")
        return True

    def __add__(self, other):
        if not self._check(other):
            return NotImplemented
        return Vector(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other):
        if not self._check(other):
            return NotImplemented
        return Vector(*(a - b for a, b in zip(self, other)))

    def __matmul__(self, other):
        if not self._check(other):
            return NotImplemented
        return sum(a * b for a, b in zip(self, other))

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(*(x * scalar for x in self))

    __rmul__ = __mul__                              # k * v == v * k

    def __truediv__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(*(x / scalar for x in self))

    def __neg__(self):
        return Vector(*(-x for x in self))

    def __abs__(self):
        return math.hypot(*self)

    def __bool__(self):
        return any(self)


if __name__ == "__main__":
    v, w = Vector(3, 4), Vector(1, 2)
    print(f"{v!r} + {w!r} = {v + w!r}")
    print(f"|v| = {abs(v)}, v·w = {v @ w}, v/3 = {v / 3:.3f}")
