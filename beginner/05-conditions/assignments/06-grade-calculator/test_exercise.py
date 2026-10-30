"""Tests for assignment 06. Run: pytest beginner/05-conditions/assignments/06-grade-calculator -v"""

import pytest


@pytest.mark.parametrize(
    "points, expected",
    [
        (100, "A"), (90, "A"), (89.5, "B"), (80, "B"), (79, "C"), (70, "C"),
        (69.9, "D"), (60, "D"), (59, "F"), (0, "F"),
    ],
)
def test_grade_boundaries(ex, points, expected):
    assert ex.grade(points) == expected


@pytest.mark.parametrize("points", [-1, 100.5, 101, 1000])
def test_grade_invalid(ex, points):
    assert ex.grade(points) == "invalid"


@pytest.mark.parametrize("points, expected", [(95, True), (60, True), (59.9, False), (0, False), (150, False), (-3, False)])
def test_passed(ex, points, expected):
    assert ex.passed(points) is expected


def test_feedback_valid(ex):
    assert ex.feedback(72) == "72 points: grade C"


def test_feedback_float(ex):
    assert ex.feedback(89.5) == "89.5 points: grade B"


def test_feedback_invalid(ex):
    assert ex.feedback(-5) == "Invalid score: -5"
