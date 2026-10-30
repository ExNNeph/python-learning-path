"""Tests for assignment 07. Run: pytest beginner/05-conditions/assignments/07-leap-years -v"""

import pytest


@pytest.mark.parametrize("year", [2024, 2000, 1600, 1996, 4])
def test_leap_years(ex, year):
    assert ex.is_leap_year(year) is True


@pytest.mark.parametrize("year", [2023, 1900, 2100, 1800, 2001])
def test_not_leap_years(ex, year):
    assert ex.is_leap_year(year) is False


@pytest.mark.parametrize(
    "month, year, expected",
    [(1, 2023, 31), (2, 2024, 29), (2, 2023, 28), (2, 1900, 28), (2, 2000, 29),
     (4, 2023, 30), (6, 2023, 30), (9, 2023, 30), (11, 2023, 30), (7, 2023, 31), (12, 2023, 31)],
)
def test_days_in_month(ex, month, year, expected):
    assert ex.days_in_month(month, year) == expected


@pytest.mark.parametrize("month", [0, 13, -1])
def test_days_in_month_invalid(ex, month):
    assert ex.days_in_month(month, 2023) is None


@pytest.mark.parametrize(
    "month, expected",
    [(12, "winter"), (1, "winter"), (2, "winter"), (3, "spring"), (5, "spring"),
     (6, "summer"), (8, "summer"), (9, "autumn"), (11, "autumn")],
)
def test_season(ex, month, expected):
    assert ex.season(month) == expected


@pytest.mark.parametrize("month", [0, 13])
def test_season_invalid(ex, month):
    assert ex.season(month) is None
