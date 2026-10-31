"""Tests for assignment 09. Run: pytest advanced/08-generators-in-depth/assignments/09-coroutine-tools -v"""

import inspect

import pytest


def drain(gen):
    """Run a generator to the end; return (items, return value)."""
    items = []
    while True:
        try:
            items.append(next(gen))
        except StopIteration as stop:
            return items, stop.value


# --- flatten -----------------------------------------------------------------

def test_flatten(ex):
    assert list(ex.flatten([1, [2, (3, "four")], [[5]]])) == [1, 2, 3, "four", 5]


def test_flatten_deep_and_mixed(ex):
    nested = [[[[1]]], (2, {3}), range(4, 6), iter([6]), b"seven", [], [[]]]
    assert list(ex.flatten(nested)) == [1, 2, 3, 4, 5, 6, b"seven"]


def test_flatten_strings_are_leaves(ex):
    assert list(ex.flatten(["ab", ["c"]])) == ["ab", "c"]


def test_flatten_is_lazy(ex):
    gen = ex.flatten([1, [2, 3]])
    assert inspect.isgenerator(gen)
    assert next(gen) == 1


# --- counted / chain_with_counts -------------------------------------------------

def test_counted(ex):
    assert drain(ex.counted("abc")) == (["a", "b", "c"], 3)
    assert drain(ex.counted([])) == ([], 0)


def test_counted_works_with_iterators(ex):
    assert drain(ex.counted(n * n for n in range(4))) == ([0, 1, 4, 9], 4)


def test_chain_with_counts(ex):
    assert drain(ex.chain_with_counts("ab", [1, 2, 3], ())) == (["a", "b", 1, 2, 3], [2, 3, 0])


def test_chain_with_counts_via_yield_from(ex):
    seen = []

    def outer():
        counts = yield from ex.chain_with_counts("xy", "z")
        seen.append(counts)

    assert list(outer()) == ["x", "y", "z"]
    assert seen == [[2, 1]]


# --- primed ------------------------------------------------------------------------

def test_primed_advances_to_first_yield(ex):
    log = []

    @ex.primed
    def echo(prefix):
        log.append("started")
        while True:
            log.append(prefix + str((yield)))

    gen = echo(">")
    assert log == ["started"]
    gen.send(1)
    assert log == ["started", ">1"]
    assert echo.__name__ == "echo"


def test_primed_returns_the_generator(ex):
    @ex.primed
    def gen():
        yield "first"
        yield "second"

    g = gen()
    assert inspect.getgeneratorstate(g) == "GEN_SUSPENDED"
    assert next(g) == "second"


# --- averager / accumulator ------------------------------------------------------

def test_averager(ex):
    avg = ex.averager()
    assert [avg.send(10), avg.send(20), avg.send(60)] == [10.0, 15.0, 30.0]


def test_averager_independent(ex):
    a, b = ex.averager(), ex.averager()
    a.send(100)
    assert b.send(1) == 1.0


def test_accumulator(ex):
    acc = ex.accumulator()
    assert [acc.send(5), acc.send(7), acc.send(None)] == [5, 12, 12]


def test_accumulator_reset(ex):
    acc = ex.accumulator()
    acc.send(5)
    acc.send(7)
    assert acc.throw(ex.Reset) == 0
    assert acc.send(1) == 1
    assert acc.throw(ex.Reset()) == 0
    assert inspect.getgeneratorstate(acc) == "GEN_SUSPENDED"


def test_accumulator_other_exceptions_end_it(ex):
    acc = ex.accumulator()
    with pytest.raises(KeyError):
        acc.throw(KeyError("boom"))
    assert inspect.getgeneratorstate(acc) == "GEN_CLOSED"


# --- pipeline ----------------------------------------------------------------------

def test_collect(ex):
    results = []
    sink = ex.collect(results)
    sink.send(1)
    sink.send("two")
    assert results == [1, "two"]


def test_grep_and_transform(ex):
    errors = []
    pipeline = ex.grep("ERROR", ex.transform(str.lower, ex.collect(errors)))
    for line in ["ERROR disk full", "INFO started", "ERROR timeout"]:
        pipeline.send(line)
    assert errors == ["error disk full", "error timeout"]


def test_broadcast(ex):
    errors, everything = [], []
    pipeline = ex.broadcast(ex.grep("ERROR", ex.collect(errors)), ex.collect(everything))
    for line in ["ERROR a", "INFO b"]:
        pipeline.send(line)
    assert errors == ["ERROR a"]
    assert everything == ["ERROR a", "INFO b"]


def test_closing_the_head_closes_everything(ex):
    sinks = [ex.collect([]), ex.collect([])]
    middle = ex.transform(abs, sinks[0])
    head = ex.broadcast(ex.grep("x", middle), sinks[1])
    head.close()
    for stage in (head, middle, *sinks):
        assert inspect.getgeneratorstate(stage) == "GEN_CLOSED"


def test_stages_are_primed_generators(ex):
    for stage in (ex.collect([]), ex.grep("a", ex.collect([])), ex.transform(str, ex.collect([])), ex.broadcast()):
        assert inspect.getgeneratorstate(stage) == "GEN_SUSPENDED"
