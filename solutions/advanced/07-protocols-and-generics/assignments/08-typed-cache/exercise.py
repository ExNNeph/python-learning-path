"""Assignment 08 · Typed cache: template solution (passes mypy --strict)."""

from __future__ import annotations

import functools
from collections import OrderedDict
from collections.abc import Callable, Iterable
from typing import Any, Generic, Literal, ParamSpec, Protocol, TypeVar, overload

K = TypeVar("K")
V = TypeVar("V")
P = ParamSpec("P")
R = TypeVar("R")


class LRUCache(Generic[K, V]):
    """A cache that forgets the least recently used entry when full."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        # OrderedDict keeps the use order for us: oldest first, newest last.
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> V | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)          # a read counts as a use
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        elif len(self._data) >= self.capacity:
            self._data.popitem(last=False)   # evict the least recently used
        self._data[key] = value

    def items(self) -> list[tuple[K, V]]:
        return list(self._data.items())

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data             # a membership test is not a use


class HasArea(Protocol):
    def area(self) -> float: ...


def total_area(shapes: Iterable[HasArea]) -> float:
    return sum(shape.area() for shape in shapes)


class SupportsLessThan(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


C = TypeVar("C", bound=SupportsLessThan)


def largest(items: Iterable[C]) -> C:
    # The bound lets max() compare; the TypeVar gives the caller back their own type.
    return max(items)


def logged(log: list[str]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            arguments = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
            log.append(f"{func.__name__}({', '.join(arguments)}) -> {result!r}")
            return result
        return wrapper
    return decorator


@overload
def convert(text: str, kind: Literal["int"]) -> int: ...
@overload
def convert(text: str, kind: Literal["float"]) -> float: ...
def convert(text: str, kind: str) -> int | float:
    if kind == "int":
        return int(text)
    if kind == "float":
        return float(text)
    raise ValueError(f"unknown kind: {kind!r}")


if __name__ == "__main__":
    cache: LRUCache[str, int] = LRUCache(2)
    for word in ["a", "b", "a", "c"]:
        if cache.get(word) is None:
            cache.put(word, len(word))
    print(cache.items())
