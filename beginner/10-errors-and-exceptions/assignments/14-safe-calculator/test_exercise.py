"""Tests for assignment 14. Run: pytest beginner/10-errors-and-exceptions/assignments/14-safe-calculator -v"""

import pytest


@pytest.mark.parametrize("text, expected", [("3", 3.0), (" 2,5 ", 2.5), ("-4", -4.0), ("1e3", 1000.0)])
def test_parse_number(ex, text, expected):
    assert ex.parse_number(text) == expected


@pytest.mark.parametrize("text", ["abc", "", "3 4", "1.2.3"])
def test_parse_number_raises_value_error(ex, text):
    with pytest.raises(ValueError) as info:
        ex.parse_number(text)
    assert str(info.value) == f"not a number: '{text}'"


@pytest.mark.parametrize("a, op, b, expected", [(3, "+", 4, 7), (3, "-", 4, -1), (3, "*", 4, 12), (7, "/", 2, 3.5)])
def test_calculate(ex, a, op, b, expected):
    assert ex.calculate(a, op, b) == expected


def test_calculate_division_by_zero(ex):
    with pytest.raises(ZeroDivisionError) as info:
        ex.calculate(1, "/", 0)
    assert str(info.value) == "cannot divide by zero"


@pytest.mark.parametrize("op", ["^", "%", "plus", ""])
def test_calculate_unknown_operator(ex, op):
    with pytest.raises(ValueError) as info:
        ex.calculate(1, op, 2)
    assert str(info.value) == f"unknown operator: '{op}'"


def test_evaluate(ex):
    assert ex.evaluate("3 * 4") == 12.0
    assert ex.evaluate("  10   /  4 ") == 2.5


@pytest.mark.parametrize("expression", ["3+4", "3 +", "", "1 + 2 + 3"])
def test_evaluate_wrong_shape(ex, expression):
    with pytest.raises(ValueError) as info:
        ex.evaluate(expression)
    assert str(info.value) == "expected: <number> <operator> <number>"


def test_evaluate_lets_errors_through(ex):
    with pytest.raises(ZeroDivisionError):
        ex.evaluate("1 / 0")
    with pytest.raises(ValueError):
        ex.evaluate("x + 1")


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("3 * 4", "12"),
        ("10 / 4", "2.5"),
        ("2,5 + 1", "3.5"),
        ("1 / 0", "Error: cannot divide by zero"),
        ("3 ^ 4", "Error: unknown operator: '^'"),
        ("three + 4", "Error: not a number: 'three'"),
        ("3+4", "Error: expected: <number> <operator> <number>"),
    ],
)
def test_safe_evaluate(ex, expression, expected):
    assert ex.safe_evaluate(expression) == expected


def test_main_loop(ex, monkeypatch, capsys):
    answers = iter(["2 + 2", "5 / 0", "quit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    ex.main()
    out = capsys.readouterr().out
    assert "4\n" in out
    assert "Error: cannot divide by zero" in out
