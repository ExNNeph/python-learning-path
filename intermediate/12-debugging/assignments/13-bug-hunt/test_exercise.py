"""Tests for assignment 13. Run: pytest intermediate/12-debugging/assignments/13-bug-hunt -v"""

import logging

import pytest


def test_average_of_positives(ex):
    assert ex.average_of_positives([3, -1, 5]) == 4.0
    assert ex.average_of_positives([2.5]) == 2.5


def test_average_of_positives_without_positives(ex):
    assert ex.average_of_positives([]) == 0.0
    assert ex.average_of_positives([-1, 0]) == 0.0


def test_remove_short_words(ex):
    assert ex.remove_short_words(["a", "an", "the", "cat"]) == ["the", "cat"]
    assert ex.remove_short_words(["hi", "yo", "hey"], min_length=2) == ["hi", "yo", "hey"]


def test_remove_short_words_adjacent_short_words(ex):
    assert ex.remove_short_words(["ok", "no", "go", "yes"]) == ["yes"]


def test_remove_short_words_keeps_input(ex):
    words = ["a", "bird"]
    ex.remove_short_words(words)
    assert words == ["a", "bird"]


def test_add_tag(ex):
    assert ex.add_tag("x", ["a"]) == ["a", "x"]


def test_add_tag_default_is_fresh(ex):
    assert ex.add_tag("first") == ["first"]
    assert ex.add_tag("second") == ["second"]


def test_make_grid(ex):
    assert ex.make_grid(2, 3) == [[0, 0, 0], [0, 0, 0]]
    assert ex.make_grid(1, 2, fill=".") == [[".", "."]]


def test_make_grid_rows_are_independent(ex):
    grid = ex.make_grid(3, 2)
    grid[0][0] = 9
    assert grid == [[9, 0], [0, 0], [0, 0]]


@pytest.mark.parametrize("items, target, expected", [
    ([5, 7, 9], 5, 0), ([5, 7, 9], 9, 2), ([5, 7, 5], 5, 0), ([5], 5, 0), ([], 5, -1), ([1, 2], 3, -1),
])
def test_find_index(ex, items, target, expected):
    assert ex.find_index(items, target) == expected


def test_parse_config(ex):
    text = "# settings\nhost = example.com\n\nport=8080\n"
    assert ex.parse_config(text) == {"host": "example.com", "port": "8080"}


def test_parse_config_value_with_equals(ex):
    assert ex.parse_config("url = https://x.org/?a=1&b=2") == {"url": "https://x.org/?a=1&b=2"}


@pytest.mark.parametrize("price, percent, expected", [(100, 25, 75.0), (19.99, 10, 17.99), (9.99, 0, 9.99), (5, 100, 0.0)])
def test_apply_discount(ex, price, percent, expected):
    assert ex.apply_discount(price, percent) == expected


@pytest.mark.parametrize("weight, expected", [(0.5, 4.99), (1, 6.99), (4.9, 6.99), (5, 6.99), (7, 7.99), (10.5, 9.74)])
def test_shipping_cost(ex, weight, expected):
    assert ex.shipping_cost(weight) == expected


@pytest.mark.parametrize("weight", [0, -1])
def test_shipping_cost_invalid(ex, weight):
    with pytest.raises(ValueError):
        ex.shipping_cost(weight)


def test_make_multipliers(ex):
    functions = ex.make_multipliers(4)
    assert [f(10) for f in functions] == [0, 10, 20, 30]
    assert ex.make_multipliers(0) == []


def test_count_words(ex):
    counts = ex.count_words("The cat saw the dog. THE end!")
    assert counts["the"] == 3
    assert counts["dog"] == 1
    assert "The" not in counts
    assert "" not in counts


def test_process_orders_total(ex):
    orders = [{"id": 1, "amount": 20}, {"id": 2}, {"id": 3, "amount": -5}, {"id": 4, "amount": 2.5}]
    assert ex.process_orders(orders) == 22.5


def test_process_orders_logs_warnings(ex, caplog):
    orders = [{"id": 1, "amount": 20}, {"id": 2}, {"id": 3, "amount": 0}]
    with caplog.at_level(logging.WARNING):
        ex.process_orders(orders)
    assert [(r.levelname, r.getMessage()) for r in caplog.records] == [
        ("WARNING", "skipping order 2: missing amount"),
        ("WARNING", "skipping order 3: amount must be positive"),
    ]


def test_process_orders_prints_nothing(ex, capsys):
    ex.process_orders([{"id": 2}])
    assert capsys.readouterr().out == ""
