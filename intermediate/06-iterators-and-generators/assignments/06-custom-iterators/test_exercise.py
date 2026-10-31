"""Tests for assignment 06. Run: pytest intermediate/06-iterators-and-generators/assignments/06-custom-iterators -v"""

import pytest


def test_countdown(ex):
    assert list(ex.Countdown(3)) == [3, 2, 1]
    assert list(ex.Countdown(0)) == []
    assert list(ex.Countdown(-2)) == []


def test_countdown_is_an_iterator(ex):
    countdown = ex.Countdown(2)
    assert iter(countdown) is countdown
    assert next(countdown) == 2
    assert next(countdown) == 1
    with pytest.raises(StopIteration):
        next(countdown)


def test_countdown_is_single_use(ex):
    countdown = ex.Countdown(2)
    assert list(countdown) == [2, 1]
    assert list(countdown) == []


def test_countdown_works_with_builtins(ex):
    assert sum(ex.Countdown(4)) == 10
    assert max(ex.Countdown(4)) == 4
    assert 2 in ex.Countdown(3)


def test_float_range(ex):
    assert list(ex.FloatRange(0, 1, 0.25)) == [0.0, 0.25, 0.5, 0.75]
    assert list(ex.FloatRange(1, 4)) == [1.0, 2.0, 3.0]


def test_float_range_no_drift(ex):
    values = list(ex.FloatRange(0, 1, 0.1))
    assert len(values) == 10
    assert values[3] == pytest.approx(0.3)
    assert values[-1] == pytest.approx(0.9)


def test_float_range_empty(ex):
    assert list(ex.FloatRange(5, 5)) == []
    assert list(ex.FloatRange(5, 1)) == []
    assert len(ex.FloatRange(5, 1)) == 0


def test_float_range_len(ex):
    assert len(ex.FloatRange(0, 1, 0.25)) == 4
    assert len(ex.FloatRange(0, 1, 0.3)) == 4


def test_float_range_is_reusable(ex):
    r = ex.FloatRange(0, 1, 0.5)
    assert list(r) == [0.0, 0.5]
    assert list(r) == [0.0, 0.5]
    assert iter(r) is not iter(r)


@pytest.mark.parametrize("step", [0, -0.5])
def test_float_range_bad_step(ex, step):
    with pytest.raises(ValueError):
        ex.FloatRange(0, 1, step)


def test_peekable_next(ex):
    p = ex.Peekable("abc")
    assert iter(p) is p
    assert [next(p), next(p), next(p)] == ["a", "b", "c"]
    with pytest.raises(StopIteration):
        next(p)


def test_peek_does_not_consume(ex):
    p = ex.Peekable([1, 2])
    assert p.peek() == 1
    assert p.peek() == 1
    assert next(p) == 1
    assert p.peek() == 2
    assert list(p) == [2]


def test_peek_at_the_end(ex):
    p = ex.Peekable([])
    with pytest.raises(StopIteration):
        p.peek()
    assert p.peek("end") == "end"
    assert p.peek(None) is None


def test_peek_handles_none_items(ex):
    p = ex.Peekable([None, 0])
    assert p.peek("default") is None
    assert next(p) is None
    assert p.peek("default") == 0
    assert list(p) == [0]


def test_peekable_is_lazy(ex):
    pulled = []

    def numbers():
        for n in range(1_000_000):
            pulled.append(n)
            yield n

    p = ex.Peekable(numbers())
    p.peek()
    next(p)
    p.peek()
    assert pulled == [0, 1]
