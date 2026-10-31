"""Tests for assignment 10. Run: pytest advanced/09-functional-tools/assignments/10-serializer -v"""

import copy
import datetime
import json
from collections import OrderedDict
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

import pytest


# --- to_jsonable -------------------------------------------------------------

@pytest.mark.parametrize("value", [None, True, 0, -3, 2.5, "text", ""])
def test_scalars_unchanged(ex, value):
    result = ex.to_jsonable(value)
    assert result == value and type(result) is type(value)


def test_containers(ex):
    assert ex.to_jsonable((1, [2, (3,)])) == [1, [2, [3]]]
    assert ex.to_jsonable({1: "a", "b": (2,)}) == {"1": "a", "b": [2]}
    assert ex.to_jsonable(OrderedDict(x=1)) == {"x": 1}
    assert ex.to_jsonable({"c", "a", "b"}) == ["a", "b", "c"]
    assert ex.to_jsonable(frozenset({3, 1})) == [1, 3]


def test_dates_and_decimals(ex):
    data = {"when": datetime.date(2026, 10, 31), "at": datetime.datetime(2026, 10, 31, 9, 30), "price": Decimal("9.90")}
    assert ex.to_jsonable(data) == {"when": "2026-10-31", "at": "2026-10-31T09:30:00", "price": "9.90"}


def test_enum(ex):
    class Color(Enum):
        RED = "red"
        LEVEL = (1, 2)

    assert ex.to_jsonable([Color.RED, Color.LEVEL]) == ["red", [1, 2]]


def test_dataclass(ex):
    @dataclass
    class Item:
        name: str
        added: datetime.date
        tags: set

    @dataclass
    class Order:
        items: list

    order = Order([Item("pen", datetime.date(2026, 1, 2), {"b", "a"})])
    assert ex.to_jsonable(order) == {"items": [{"name": "pen", "added": "2026-01-02", "tags": ["a", "b"]}]}


def test_unknown_type(ex):
    class Foo:
        pass

    with pytest.raises(TypeError, match="cannot convert Foo to JSON"):
        ex.to_jsonable({"x": [Foo()]})
    with pytest.raises(TypeError, match="cannot convert complex"):
        ex.to_jsonable(1j)


def test_is_open_for_new_types(ex):
    class Money:
        def __init__(self, cents):
            self.cents = cents

    @ex.to_jsonable.register
    def _(value: Money):
        return {"cents": value.cents}

    assert ex.to_jsonable([Money(150)]) == [{"cents": 150}]


def test_output_is_valid_json(ex):
    data = {"d": datetime.date(2026, 1, 1), "s": {1, 2}, "n": None, "t": (Decimal("1.5"),)}
    assert json.loads(json.dumps(ex.to_jsonable(data))) == {"d": "2026-01-01", "s": [1, 2], "n": None, "t": ["1.5"]}


def test_does_not_change_input(ex):
    data = {"a": [1, {2, 3}], "b": (4,)}
    before = copy.deepcopy(data)
    ex.to_jsonable(data)
    assert data == before


# --- Version ------------------------------------------------------------------

def test_version_ordering(ex):
    versions = [ex.Version(v) for v in ["1.10", "1.9.3", "1.9", "0.99", "2"]]
    assert [str(v) for v in sorted(versions)] == ["0.99", "1.9", "1.9.3", "1.10", "2"]


def test_version_all_comparisons(ex):
    a, b = ex.Version("1.2"), ex.Version("1.10")
    assert a < b and a <= b and b > a and b >= a and a != b
    assert not (a > b) and not (a >= b)


def test_version_trailing_zeros(ex):
    assert ex.Version("1.2") == ex.Version("1.2.0.0")
    assert ex.Version("2.0") == ex.Version("2")
    assert ex.Version("1.0.1") > ex.Version("1")
    assert ex.Version("0") == ex.Version("0.0")


def test_version_hash(ex):
    assert len({ex.Version("1.2"), ex.Version("1.2.0"), ex.Version("1.3")}) == 2


def test_version_text(ex):
    v = ex.Version("1.10.0")
    assert repr(v) == "Version('1.10.0')"
    assert str(v) == "1.10.0"


@pytest.mark.parametrize("text", ["", "1..2", "1.a", "-1", "1.", " 1", "v1"])
def test_version_invalid(ex, text):
    with pytest.raises(ValueError):
        ex.Version(text)


def test_version_other_types(ex):
    assert ex.Version("1") != "1"
    assert ex.Version("1").__eq__("1") is NotImplemented
    with pytest.raises(TypeError):
        ex.Version("1") < "2"


def test_version_uses_total_ordering(ex):
    assert "__lt__" in vars(ex.Version)
    assert ex.Version.__ge__ is not object.__ge__


# --- compose -------------------------------------------------------------------

def test_compose_order(ex):
    assert ex.compose(lambda x: x * 2, lambda x: x + 1)(5) == 12
    assert ex.compose(lambda x: x + 1, lambda x: x * 2)(5) == 11


def test_compose_strings(ex):
    slug = ex.compose("-".join, str.split, str.lower)
    assert slug("Functional Tools Rock") == "functional-tools-rock"


def test_compose_identity_and_single(ex):
    assert ex.compose()("same") == "same"
    assert ex.compose(abs)(-3) == 3


def test_compose_is_reusable(ex):
    inc = ex.compose(lambda x: x + 1)
    assert [inc(n) for n in range(3)] == [1, 2, 3]


# --- update_in -------------------------------------------------------------------

def test_update_in(ex):
    config = {"db": {"ports": [5432, 5433]}, "debug": False}
    new = ex.update_in(config, ["db", "ports", 1], lambda p: p + 1)
    assert new == {"db": {"ports": [5432, 5434]}, "debug": False}
    assert config == {"db": {"ports": [5432, 5433]}, "debug": False}


def test_update_in_shares_untouched_parts(ex):
    data = {"a": {"x": 1}, "b": {"y": [1, 2]}, "c": [{"z": 0}, {"z": 1}]}
    new = ex.update_in(data, ["c", 1, "z"], lambda z: z + 10)
    assert new["a"] is data["a"]
    assert new["b"] is data["b"]
    assert new["c"][0] is data["c"][0]
    assert new["c"] is not data["c"]
    assert new["c"][1] == {"z": 11} and data["c"][1] == {"z": 1}


def test_update_in_negative_index(ex):
    assert ex.update_in([1, 2, 3], [-1], str) == [1, 2, "3"]


def test_update_in_empty_path(ex):
    assert ex.update_in(5, [], lambda n: n * 2) == 10
    assert ex.update_in({"a": 1}, (), len) == 1


def test_update_in_tuple_path_and_new_types(ex):
    assert ex.update_in({"a": [0]}, ("a", 0), lambda _: "zero") == {"a": ["zero"]}


def test_update_in_missing(ex):
    data = {"a": [1]}
    with pytest.raises(KeyError):
        ex.update_in(data, ["b"], str)
    with pytest.raises(IndexError):
        ex.update_in(data, ["a", 5], str)
    assert data == {"a": [1]}
