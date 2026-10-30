"""Tests for assignment 16. Run: pytest beginner/12-modules-and-imports/assignments/16-stdlib-tour -v"""

from datetime import date

import pytest


@pytest.mark.parametrize("radius, expected", [(2, 12.57), (1, 3.14), (0, 0), (10, 314.16)])
def test_circle_area(ex, radius, expected):
    assert ex.circle_area(radius) == expected


@pytest.mark.parametrize("a, b, expected", [(3, 4, 5.0), (5, 12, 13.0), (1, 1, 1.41)])
def test_hypotenuse(ex, a, b, expected):
    assert ex.hypotenuse(a, b) == expected


@pytest.mark.parametrize(
    "target, expected",
    [("2026-12-24", 55), ("2026-10-30", 0), ("2026-10-01", -29), ("2027-10-30", 365)],
)
def test_days_until(ex, target, expected):
    assert ex.days_until(target, date(2026, 10, 30)) == expected


@pytest.mark.parametrize(
    "text, expected",
    [("2026-12-24", "Thursday"), ("2026-10-30", "Friday"), ("2000-01-01", "Saturday"), ("1969-07-20", "Sunday")],
)
def test_weekday(ex, text, expected):
    assert ex.weekday(text) == expected


def test_roll_dice_length_and_range(ex):
    rolls = ex.roll_dice(200, seed=1)
    assert len(rolls) == 200
    assert all(1 <= roll <= 6 for roll in rolls)
    assert set(rolls) == {1, 2, 3, 4, 5, 6}


def test_roll_dice_custom_sides(ex):
    rolls = ex.roll_dice(100, sides=20, seed=7)
    assert all(1 <= roll <= 20 for roll in rolls)


def test_roll_dice_same_seed_same_result(ex):
    assert ex.roll_dice(10, seed=42) == ex.roll_dice(10, seed=42)


def test_roll_dice_different_seeds_differ(ex):
    assert ex.roll_dice(10, seed=1) != ex.roll_dice(10, seed=2)


def test_roll_dice_zero(ex):
    assert ex.roll_dice(0) == []


def test_summary_stats(ex):
    assert ex.summary_stats([2, 4, 4, 4, 5, 5, 7, 9]) == {"mean": 5, "median": 4.5, "stdev": 2.14}


def test_summary_stats_rounding(ex):
    assert ex.summary_stats([1, 2, 2]) == {"mean": 1.67, "median": 2, "stdev": 0.58}


@pytest.mark.parametrize(
    "text, expected",
    [("Hello, World!", "l"), ("AAbb", "a"), ("bbAA", "b"), ("Mississippi", "i"), ("x1 2 3!!", "x")],
)
def test_most_common_letter(ex, text, expected):
    assert ex.most_common_letter(text) == expected
