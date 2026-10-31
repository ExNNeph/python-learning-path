"""Assignment 10 · Serializer.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/09-functional-tools/assignments/10-serializer -v
"""

import dataclasses
import datetime
from collections.abc import Mapping
from decimal import Decimal
from enum import Enum
from functools import reduce, singledispatch, total_ordering


def to_jsonable(value):
    """TODO: make this a singledispatch function (see the README for the table of types)."""
    raise NotImplementedError


class Version:
    """A version number like "1.10.2". TODO: @total_ordering with __eq__, __lt__ and __hash__."""

    def __init__(self, text):
        raise NotImplementedError


def compose(*funcs):
    """compose(f, g, h)(x) == f(g(h(x))). Use functools.reduce."""
    raise NotImplementedError


def update_in(data, path, func):
    """Return a new structure with func applied at path; never change data."""
    raise NotImplementedError


if __name__ == "__main__":
    import json

    release = {"version": str(Version("1.10.0")), "date": datetime.date(2026, 10, 31), "tags": {"stable"}}
    print(json.dumps(to_jsonable(release)))
