"""Tests for assignment 08. Run: pytest intermediate/07-standard-library-toolbox/assignments/08-power-tools -v"""

import pytest


def test_top_words(ex):
    assert ex.top_words("the cat and The hat and THE bat", 2) == [("the", 3), ("and", 2)]
    assert ex.top_words("", 3) == []


def test_top_words_ties_keep_first_appearance(ex):
    assert ex.top_words("b a b a c", 3) == [("b", 2), ("a", 2), ("c", 1)]


def test_group_by_length(ex):
    assert ex.group_by_length(["hi", "tea", "go", "cup"]) == {2: ["hi", "go"], 3: ["tea", "cup"]}
    assert ex.group_by_length([]) == {}


def test_group_by_length_returns_plain_dict(ex):
    groups = ex.group_by_length(["hi"])
    assert type(groups) is dict
    with pytest.raises(KeyError):
        groups[5]


def test_totals_by_customer(ex):
    orders = [
        {"customer": "grace", "amount": 10},
        {"customer": "ada", "amount": 30},
        {"customer": "linus", "amount": 7},
        {"customer": "ada", "amount": 5},
    ]
    result = ex.totals_by_customer(orders)
    assert result == {"ada": 35, "grace": 10, "linus": 7}
    assert list(result) == ["ada", "grace", "linus"]


def test_totals_by_customer_does_not_change_input(ex):
    orders = [{"customer": "b", "amount": 1}, {"customer": "a", "amount": 2}]
    ex.totals_by_customer(orders)
    assert [o["customer"] for o in orders] == ["b", "a"]


def test_last_n(ex):
    assert ex.last_n(range(1_000_000), 3) == [999997, 999998, 999999]
    assert ex.last_n("ab", 5) == ["a", "b"]
    assert ex.last_n(iter([1, 2, 3]), 2) == [2, 3]


def test_pairs(ex):
    assert ex.pairs("ABC") == [("A", "B"), ("A", "C"), ("B", "C")]
    assert ex.pairs([1]) == []
    assert len(ex.pairs(range(10))) == 45


@pytest.mark.parametrize("steps, expected", [(-1, 0), (0, 1), (1, 1), (2, 2), (3, 4), (4, 7), (10, 274)])
def test_count_paths_small(ex, steps, expected):
    assert ex.count_paths(steps) == expected


def test_count_paths_is_cached(ex):
    assert hasattr(ex.count_paths, "cache_info"), "decorate count_paths with @lru_cache or @cache"


def test_count_paths_large(ex):
    assert hasattr(ex.count_paths, "cache_info"), "without a cache this test would run for ages"
    a, b, c = 0, 0, 1        # tribonacci, computed independently
    for _ in range(200):
        a, b, c = b, c, a + b + c
    assert ex.count_paths(200) == c


def test_weekdays_between(ex):
    assert ex.weekdays_between("2026-10-30", "2026-11-02") == 2     # Fri .. Mon
    assert ex.weekdays_between("2026-11-02", "2026-11-08") == 5     # a full week
    assert ex.weekdays_between("2026-11-01", "2026-11-30") == 21
    assert ex.weekdays_between("2026-10-31", "2026-10-31") == 0     # a Saturday
    assert ex.weekdays_between("2026-11-02", "2026-11-02") == 1     # a Monday


def test_weekdays_between_reversed(ex):
    assert ex.weekdays_between("2026-11-08", "2026-11-02") == 0


@pytest.mark.parametrize("start, end, expected", [("09:15", "11:00", 105), ("00:00", "23:59", 1439), ("12:00", "12:00", 0)])
def test_duration_minutes(ex, start, end, expected):
    assert ex.duration_minutes(start, end) == expected


def test_duration_minutes_reversed(ex):
    with pytest.raises(ValueError):
        ex.duration_minutes("11:00", "09:15")


@pytest.mark.parametrize("bad", ["9.15", "25:00", "noon"])
def test_duration_minutes_bad_format(ex, bad):
    with pytest.raises(ValueError):
        ex.duration_minutes(bad, "23:00")
