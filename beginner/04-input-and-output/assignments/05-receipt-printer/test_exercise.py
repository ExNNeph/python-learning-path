"""Tests for assignment 05. Run: pytest beginner/04-input-and-output/assignments/05-receipt-printer -v"""

import pytest


@pytest.mark.parametrize("text, expected", [("3.50", 3.5), (" 3,50 ", 3.5), ("12", 12.0), ("0,99\n", 0.99)])
def test_parse_price(ex, text, expected):
    assert ex.parse_price(text) == expected


def test_parse_price_returns_float(ex):
    assert type(ex.parse_price("12")) is float


def test_format_line_default_width(ex):
    assert ex.format_line("Coffee x3", 10.5) == "Coffee x3..........10.50"


def test_format_line_is_always_width_long(ex):
    assert len(ex.format_line("Tea", 2)) == 24


def test_format_line_custom_width(ex):
    assert ex.format_line("TOTAL", 7, width=12) == "TOTAL...7.00"


def test_format_line_rounds_to_two_decimals(ex):
    assert ex.format_line("Cake", 4.199) == "Cake................4.20"


def test_main_prints_receipt(ex, monkeypatch, capsys):
    answers = iter(["Coffee", "3,50", "3"])
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr("builtins.input", fake_input)
    ex.main()

    assert prompts == ["Item: ", "Price: ", "Quantity: "]
    assert capsys.readouterr().out == (
        "Coffee x3..........10.50\n"
        "------------------------\n"
        "TOTAL..............10.50\n"
    )
