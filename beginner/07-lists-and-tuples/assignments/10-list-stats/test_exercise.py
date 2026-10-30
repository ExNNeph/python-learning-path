"""Tests for assignment 10. Run: pytest beginner/07-lists-and-tuples/assignments/10-list-stats -v"""

import pytest


@pytest.mark.parametrize("numbers, expected", [([1, 2, 3, 4], 2.5), ([5], 5), ([-1, 1], 0), ([2, 2, 2], 2)])
def test_mean(ex, numbers, expected):
    assert ex.mean(numbers) == expected


@pytest.mark.parametrize("numbers, expected", [([5, 1, 3], 3), ([4, 1, 3, 2], 2.5), ([7], 7), ([1, 2], 1.5), ([9, 9, 1, 1, 5], 5)])
def test_median(ex, numbers, expected):
    assert ex.median(numbers) == expected


@pytest.mark.parametrize("numbers, expected", [([4, -2, 9, 0], (-2, 9)), ([7], (7, 7)), ([-5, -2, -9], (-9, -2)), ([3, 3], (3, 3))])
def test_min_max(ex, numbers, expected):
    assert ex.min_max(numbers) == expected


@pytest.mark.parametrize("func", ["mean", "median", "min_max"])
def test_empty_list_gives_none(ex, func):
    assert getattr(ex, func)([]) is None


@pytest.mark.parametrize("numbers, expected", [([1, 2, 3, 4], [1, 3, 6, 10]), ([], []), ([5, -5, 5], [5, 0, 5])])
def test_running_total(ex, numbers, expected):
    assert ex.running_total(numbers) == expected


@pytest.mark.parametrize(
    "items, expected",
    [(["b", "a", "b", "c", "a"], ["b", "a", "c"]), ([1, 1, 1], [1]), ([], []), ([3, 2, 1], [3, 2, 1])],
)
def test_remove_duplicates(ex, items, expected):
    assert ex.remove_duplicates(items) == expected


@pytest.mark.parametrize("numbers, n, expected", [([70, 95, 82, 61], 2, [95, 82]), ([1, 2], 5, [2, 1]), ([4, 4, 1], 2, [4, 4]), ([3, 1], 0, [])])
def test_top_n(ex, numbers, n, expected):
    assert ex.top_n(numbers, n) == expected


@pytest.mark.parametrize(
    "func, args",
    [("mean", ()), ("median", ()), ("min_max", ()), ("running_total", ()), ("remove_duplicates", ()), ("top_n", (2,))],
)
def test_input_list_is_not_changed(ex, func, args):
    numbers = [70, 95, 82, 61, 95]
    getattr(ex, func)(numbers, *args)
    assert numbers == [70, 95, 82, 61, 95]


def test_results_are_new_lists(ex):
    numbers = [1, 2, 3]
    assert ex.running_total(numbers) is not numbers
    assert ex.remove_duplicates(numbers) is not numbers
    assert ex.top_n(numbers, 3) is not numbers
