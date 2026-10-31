"""Assignment 10 · Serializer: template solution."""

import dataclasses
import datetime
from collections.abc import Mapping
from decimal import Decimal
from enum import Enum
from functools import reduce, singledispatch, total_ordering


# --- to_jsonable ----------------------------------------------------------------

@singledispatch
def to_jsonable(value):
    # Dataclasses share no base class, so singledispatch cannot select them: check in the fallback.
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: to_jsonable(getattr(value, f.name)) for f in dataclasses.fields(value)}
    raise TypeError(f"cannot convert {type(value).__name__} to JSON")


@to_jsonable.register(type(None))
@to_jsonable.register(bool)
@to_jsonable.register(int)
@to_jsonable.register(float)
@to_jsonable.register(str)
def _(value):
    return value


@to_jsonable.register(list)
@to_jsonable.register(tuple)
def _(value):
    return [to_jsonable(item) for item in value]


@to_jsonable.register(Mapping)        # an ABC: covers dict, OrderedDict, MappingProxyType, ...
def _(value):
    return {str(key): to_jsonable(item) for key, item in value.items()}


@to_jsonable.register(set)
@to_jsonable.register(frozenset)
def _(value):
    return sorted(to_jsonable(item) for item in value)


@to_jsonable.register(datetime.date)  # datetime.datetime is a subclass: handled too
def _(value):
    return value.isoformat()


@to_jsonable.register(Decimal)
def _(value):
    return str(value)                 # float(value) would lose the exact digits


@to_jsonable.register(Enum)
def _(value):
    return to_jsonable(value.value)


# --- Version --------------------------------------------------------------------

@total_ordering
class Version:
    def __init__(self, text):
        parts = text.split(".")
        if not all(part.isdigit() for part in parts):
            raise ValueError(f"invalid version: {text!r}")
        self.text = text
        numbers = [int(part) for part in parts]
        while len(numbers) > 1 and numbers[-1] == 0:
            numbers.pop()             # 1.2.0 == 1.2: trailing zeros do not count
        self._key = tuple(numbers)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._key == other._key

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._key < other._key  # tuples compare element by element: 10 > 9

    def __hash__(self):
        return hash(self._key)         # the same key as __eq__

    def __repr__(self):
        return f"Version({self.text!r})"

    def __str__(self):
        return self.text


# --- compose / update_in --------------------------------------------------------

def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, lambda x: x)


def update_in(data, path, func):
    if not path:
        return func(data)
    key, rest = path[0], path[1:]
    child = update_in(data[key], rest, func)     # KeyError / IndexError surface here
    if isinstance(data, list):
        index = range(len(data))[key]            # normalise negative indexes
        return [*data[:index], child, *data[index + 1:]]
    return {**data, key: child}                  # a new dict; untouched values are shared, not copied


if __name__ == "__main__":
    import json

    release = {"version": str(Version("1.10.0")), "date": datetime.date(2026, 10, 31), "tags": {"stable"}}
    print(json.dumps(to_jsonable(release)))
