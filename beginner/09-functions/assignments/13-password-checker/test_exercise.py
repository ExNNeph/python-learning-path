"""Tests for assignment 13. Run: pytest beginner/09-functions/assignments/13-password-checker -v"""

import pytest


@pytest.mark.parametrize(
    "func, yes, no",
    [
        ("has_digit", "abc1", "abc"),
        ("has_upper", "abC", "abc1"),
        ("has_lower", "ABc", "ABC1"),
        ("has_special", "ab c", "abc123"),
        ("has_special", "a!", "Abc"),
    ],
)
def test_helpers(ex, func, yes, no):
    assert getattr(ex, func)(yes) is True
    assert getattr(ex, func)(no) is False


@pytest.mark.parametrize("func", ["has_digit", "has_upper", "has_lower", "has_special"])
def test_helpers_empty_string(ex, func):
    assert getattr(ex, func)("") is False


def test_problems_too_short_only(ex):
    assert ex.password_problems("Secr3t!") == ["at least 8 characters"]


def test_problems_in_order(ex):
    assert ex.password_problems("password") == ["a digit", "an uppercase letter", "a special character"]


def test_problems_all(ex):
    assert ex.password_problems("") == [
        "at least 8 characters",
        "a digit",
        "an uppercase letter",
        "a lowercase letter",
        "a special character",
    ]


def test_problems_none(ex):
    assert ex.password_problems("Tr0ub4dor&3") == []


def test_problems_custom_min_length(ex):
    assert ex.password_problems("Secr3t!", min_length=6) == []
    assert ex.password_problems("Tr0ub4dor&3", min_length=12) == ["at least 12 characters"]


def test_problems_returns_a_fresh_list_each_call(ex):
    first = ex.password_problems("password")
    second = ex.password_problems("password")
    assert first == second
    assert first is not second


@pytest.mark.parametrize(
    "password, expected",
    [("Tr0ub4dor&3", "strong"), ("Secr3t!", "medium"), ("secr3t!x", "medium"), ("password", "weak"), ("", "weak")],
)
def test_strength(ex, password, expected):
    assert ex.strength(password) == expected


def test_strength_passes_min_length(ex):
    assert ex.strength("Secr3t!", min_length=4) == "strong"


def test_check_all(ex):
    assert ex.check_all(["Tr0ub4dor&3", "hello"], min_length=10) == {"Tr0ub4dor&3": "strong", "hello": "weak"}


def test_check_all_default_length(ex):
    assert ex.check_all(["Secr3t!"]) == {"Secr3t!": "medium"}


def test_check_all_empty(ex):
    assert ex.check_all([]) == {}
