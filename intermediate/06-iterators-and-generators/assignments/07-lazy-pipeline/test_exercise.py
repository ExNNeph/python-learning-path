"""Tests for assignment 07. Run: pytest intermediate/06-iterators-and-generators/assignments/07-lazy-pipeline -v"""

import inspect
import itertools

import pytest

GENERATORS = ["clean_lines", "parse_readings", "running_total", "chunked", "sliding_window", "fibonacci", "flatten"]


@pytest.mark.parametrize("name", GENERATORS)
def test_is_a_generator_function(ex, name):
    assert inspect.isgeneratorfunction(getattr(ex, name))


class Exploding:
    """An iterable that yields `good` items and then fails: proves a function is lazy."""

    def __init__(self, good):
        self.good = good

    def __iter__(self):
        yield from self.good
        raise AssertionError("pulled too many items: the function is not lazy")


def test_clean_lines(ex):
    lines = ["  # boot", "kitchen,21.5 ", "", "   ", "garage,oops", "#", "x # not a comment"]
    assert list(ex.clean_lines(lines)) == ["kitchen,21.5", "garage,oops", "x # not a comment"]


def test_clean_lines_is_lazy(ex):
    assert next(ex.clean_lines(Exploding(["", "a"]))) == "a"


def test_parse_readings(ex):
    lines = ["kitchen,21.5", "garage,oops", "a,b,c", "cellar,9", "nocomma", "attic,-3.25"]
    assert list(ex.parse_readings(lines)) == [("kitchen", 21.5), ("cellar", 9.0), ("attic", -3.25)]


def test_parse_readings_is_lazy(ex):
    assert next(ex.parse_readings(Exploding(["bad", "ok,1"]))) == ("ok", 1.0)


def test_running_total(ex):
    assert list(ex.running_total([1, 2, 3])) == [1, 3, 6]
    assert list(ex.running_total([])) == []
    assert list(itertools.islice(ex.running_total(itertools.count(1)), 4)) == [1, 3, 6, 10]


def test_chunked(ex):
    assert list(ex.chunked("abcdefg", 3)) == [["a", "b", "c"], ["d", "e", "f"], ["g"]]
    assert list(ex.chunked([1, 2], 2)) == [[1, 2]]
    assert list(ex.chunked([], 2)) == []


def test_chunked_chunks_are_independent(ex):
    first, second = ex.chunked([1, 2, 3, 4], 2)
    first.append(99)
    assert second == [3, 4]


def test_chunked_infinite(ex):
    assert next(ex.chunked(itertools.count(), 3)) == [0, 1, 2]


@pytest.mark.parametrize("size", [0, -1])
def test_chunked_bad_size(ex, size):
    with pytest.raises(ValueError):
        list(ex.chunked([1, 2], size))


def test_sliding_window(ex):
    assert list(ex.sliding_window([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(ex.sliding_window("abc", 3)) == [("a", "b", "c")]
    assert list(ex.sliding_window([1, 2], 3)) == []


def test_sliding_window_is_lazy(ex):
    assert next(ex.sliding_window(Exploding([1, 2]), 2)) == (1, 2)


def test_fibonacci(ex):
    assert list(itertools.islice(ex.fibonacci(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_flatten(ex):
    assert list(ex.flatten([1, [2, (3, [4])], 5])) == [1, 2, 3, 4, 5]
    assert list(ex.flatten([[], [[]], ()])) == []
    assert list(ex.flatten(["ab", ["cd"]])) == ["ab", "cd"]


def test_take(ex):
    assert ex.take([1, 2, 3], 2) == [1, 2]
    assert ex.take([1, 2], 5) == [1, 2]
    assert ex.take([1, 2], 0) == []
    assert ex.take(itertools.count(), 3) == [0, 1, 2]


def test_take_pulls_exactly_n_items(ex):
    assert ex.take(Exploding([1, 2, 3]), 3) == [1, 2, 3]


def test_take_returns_a_list(ex):
    assert isinstance(ex.take("abc", 2), list)


def test_pipeline_on_endless_stream(ex):
    readings = ex.parse_readings(ex.clean_lines(ex.sensor_stream()))
    first = ex.take(readings, 20)
    assert len(first) == 20
    assert all(sensor == "kitchen" and 18 <= value <= 22 for sensor, value in first)


def test_running_total_of_fibonacci(ex):
    assert ex.take(ex.running_total(ex.fibonacci()), 5) == [0, 1, 2, 4, 7]
