"""Tests for assignment 02. Run: pytest intermediate/02-functions-in-depth/assignments/02-function-toolkit -v"""

import pytest


def test_format_price_defaults(ex):
    assert ex.format_price(12.5) == "12.50 EUR"
    assert ex.format_price(0) == "0.00 EUR"


def test_format_price_options(ex):
    assert ex.format_price(3, currency="USD", decimals=0) == "3 USD"
    assert ex.format_price(2.34567, decimals=3) == "2.346 EUR"


def test_format_price_amount_is_positional_only(ex):
    with pytest.raises(TypeError):
        ex.format_price(amount=5)


def test_format_price_options_are_keyword_only(ex):
    with pytest.raises(TypeError):
        ex.format_price(5, "USD")


@pytest.mark.parametrize("a, op, b, expected", [(6, "*", 7, 42), (1, "+", 2, 3), (5, "-", 8, -3), (7, "/", 2, 3.5)])
def test_calculate(ex, a, op, b, expected):
    assert ex.calculate(a, op, b) == expected


def test_calculate_unknown_operator(ex):
    with pytest.raises(ValueError, match="unknown operator: '%'"):
        ex.calculate(1, "%", 2)


def test_calculate_division_by_zero_is_not_hidden(ex):
    with pytest.raises(ZeroDivisionError):
        ex.calculate(1, "/", 0)


def test_pipeline(ex):
    clean = ex.pipeline(str.strip, str.lower, lambda s: s.replace(" ", "-"))
    assert clean("  Hello World ") == "hello-world"


def test_pipeline_order_is_left_to_right(ex):
    assert ex.pipeline(lambda n: n + 1, lambda n: n * 10)(1) == 20
    assert ex.pipeline(lambda n: n * 10, lambda n: n + 1)(1) == 11


def test_pipeline_without_functions(ex):
    assert ex.pipeline()("unchanged") == "unchanged"


def test_pipeline_is_reusable(ex):
    inc = ex.pipeline(lambda n: n + 1)
    assert [inc(n) for n in range(3)] == [1, 2, 3]


def test_make_multiplier(ex):
    double, triple = ex.make_multiplier(2), ex.make_multiplier(3)
    assert double(5) == 10
    assert triple(5) == 15
    assert double("ab") == "abab"


def test_make_counter(ex):
    tick = ex.make_counter()
    assert [tick(), tick(), tick()] == [0, 1, 2]


def test_make_counter_start_and_step(ex):
    tick = ex.make_counter(10, step=5)
    assert [tick(), tick(), tick()] == [10, 15, 20]


def test_counters_are_independent(ex):
    a, b = ex.make_counter(), ex.make_counter(100)
    a(); a()
    assert b() == 100
    assert a() == 2


def test_call_counted(ex):
    wrapped, calls = ex.call_counted(max)
    assert calls() == 0
    assert wrapped(3, 9, 4) == 9
    assert wrapped([1, -2], key=abs) == -2
    assert calls() == 2


def test_call_counted_counts_failed_calls_too(ex):
    wrapped, calls = ex.call_counted(int)
    with pytest.raises(ValueError):
        wrapped("x")
    assert calls() == 1


def test_call_counted_separate_counters(ex):
    w1, c1 = ex.call_counted(len)
    w2, c2 = ex.call_counted(len)
    w1("a"); w1("b"); w2("c")
    assert (c1(), c2()) == (2, 1)
