"""Assignment 08 · Typed cache.

Replace each `raise NotImplementedError` with your code and write the type annotations.
The file must pass:  mypy --strict advanced/07-protocols-and-generics/assignments/08-typed-cache/exercise.py
Check your work:     pytest advanced/07-protocols-and-generics/assignments/08-typed-cache -v
"""

from __future__ import annotations

import functools
from collections import OrderedDict
from collections.abc import Callable, Iterable
from typing import Any, Generic, Literal, ParamSpec, Protocol, TypeVar, overload

K = TypeVar("K")
V = TypeVar("V")


class LRUCache:
    """TODO: make this Generic[K, V]. A cache that forgets the least recently used entry when full."""

    def __init__(self, capacity):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def put(self, key, value):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __contains__(self, key):
        raise NotImplementedError


class HasArea:
    """TODO: a Protocol with area(self) -> float."""


def total_area(shapes):
    raise NotImplementedError


def largest(items):
    """The largest item. TODO: a TypeVar bound to a protocol with __lt__."""
    raise NotImplementedError


def logged(log):
    """Decorator factory: append 'name(args, kw=value) -> result' to log on every call."""
    raise NotImplementedError


def convert(text, kind):
    """kind "int" → int(text), kind "float" → float(text). TODO: two @overloads with Literal."""
    raise NotImplementedError


if __name__ == "__main__":
    cache: LRUCache[str, int] = LRUCache(2)
    for word in ["a", "b", "a", "c"]:
        if cache.get(word) is None:
            cache.put(word, len(word))
    print(cache.items())
