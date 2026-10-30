"""Tests for assignment 02. Run: pytest beginner/02-variables-and-types/assignments/02-type-detective -v"""

import pytest


@pytest.mark.parametrize(
    "value, expected",
    [(42, "int"), (4.2, "float"), ("42", "str"), (True, "bool"), (None, "NoneType")],
)
def test_type_name(ex, value, expected):
    assert ex.type_name(value) == expected


def test_describe_float(ex):
    assert ex.describe(3.5) == "3.5 is of type float"


def test_describe_text(ex):
    assert ex.describe("hi") == "hi is of type str"


def test_describe_none(ex):
    assert ex.describe(None) == "None is of type NoneType"


def test_add_numeric_strings_returns_a_number(ex):
    assert ex.add_numeric_strings("3", "4") == 7


def test_add_numeric_strings_bigger_numbers(ex):
    assert ex.add_numeric_strings("120", "80") == 200


def test_swap(ex):
    assert ex.swap(1, "a") == ("a", 1)


def test_swap_can_be_unpacked(ex):
    x, y = ex.swap("left", "right")
    assert (x, y) == ("right", "left")


def test_same_object_true(ex):
    numbers = [1, 2]
    alias = numbers
    assert ex.same_object(numbers, alias) is True


def test_same_object_false_for_equal_copies(ex):
    assert ex.same_object([1, 2], [1, 2]) is False
