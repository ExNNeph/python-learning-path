"""Tests for assignment 01. Run: pytest advanced/01-decorators/assignments/01-decorator-kit -v"""

import pytest


# --- count_calls -------------------------------------------------------------

def test_count_calls_counts(ex):
    @ex.count_calls
    def ping():
        return "pong"

    assert ping.calls == 0
    assert [ping(), ping(), ping()] == ["pong"] * 3
    assert ping.calls == 3


def test_count_calls_forwards_arguments(ex):
    @ex.count_calls
    def describe(a, b=0, *rest, sep="-"):
        return sep.join(map(str, (a, b, *rest)))

    assert describe(1, 2, 3, sep="+") == "1+2+3"
    assert describe(a=5) == "5-0"
    assert describe.calls == 2


def test_count_calls_counts_per_function(ex):
    @ex.count_calls
    def one():
        pass

    @ex.count_calls
    def two():
        pass

    one(), one(), two()
    assert (one.calls, two.calls) == (2, 1)


def test_count_calls_keeps_identity(ex):
    @ex.count_calls
    def ping():
        """Answer."""

    assert ping.__name__ == "ping"
    assert ping.__doc__ == "Answer."
    assert callable(ping.__wrapped__)


def test_count_calls_counts_failing_calls(ex):
    @ex.count_calls
    def boom():
        raise RuntimeError

    with pytest.raises(RuntimeError):
        boom()
    assert boom.calls == 1


# --- memoize -----------------------------------------------------------------

def test_memoize_caches(ex):
    computed = []

    @ex.memoize
    def square(n):
        computed.append(n)
        return n * n

    assert [square(4), square(4), square(5), square(4)] == [16, 16, 25, 16]
    assert computed == [4, 5]
    assert square.cache == {(4,): 16, (5,): 25}


def test_memoize_caches_falsy_results(ex):
    computed = []

    @ex.memoize
    def nothing(n):
        computed.append(n)
        return None

    nothing(1), nothing(1)
    assert computed == [1]


def test_memoize_cache_clear(ex):
    computed = []

    @ex.memoize
    def double(n):
        computed.append(n)
        return 2 * n

    double(1)
    double.cache_clear()
    assert double.cache == {}
    double(1)
    assert computed == [1, 1]


def test_memoize_makes_recursion_fast(ex):
    @ex.memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(90) == 2880067194370816120
    assert len(fib.cache) == 91


def test_memoize_keeps_identity(ex):
    @ex.memoize
    def square(n):
        """Square it."""
        return n * n

    assert (square.__name__, square.__doc__) == ("square", "Square it.")


# --- retry -------------------------------------------------------------------

def make_flaky(failures, error=ConnectionError):
    attempts = []

    def flaky(value="ok"):
        attempts.append(1)
        if len(attempts) <= failures:
            raise error(f"attempt {len(attempts)}")
        return value

    return flaky, attempts


def test_retry_succeeds_after_failures(ex):
    flaky, attempts = make_flaky(2)
    assert ex.retry(3)(flaky)(value="connected") == "connected"
    assert len(attempts) == 3


def test_retry_success_needs_no_retries(ex):
    flaky, attempts = make_flaky(0)
    assert ex.retry(5)(flaky)() == "ok"
    assert len(attempts) == 1


def test_retry_reraises_the_last_error(ex):
    flaky, attempts = make_flaky(10)
    with pytest.raises(ConnectionError, match="attempt 3"):
        ex.retry(3)(flaky)()
    assert len(attempts) == 3


def test_retry_only_listed_exceptions(ex):
    flaky, attempts = make_flaky(1, error=KeyError)
    with pytest.raises(KeyError):
        ex.retry(3, exceptions=(ConnectionError,))(flaky)()
    assert len(attempts) == 1


def test_retry_tuple_of_exceptions(ex):
    flaky, attempts = make_flaky(2, error=TimeoutError)
    assert ex.retry(3, exceptions=(ConnectionError, TimeoutError))(flaky)() == "ok"


def test_retry_validates_times_at_decoration(ex):
    with pytest.raises(ValueError):
        ex.retry(0)


def test_retry_keeps_identity(ex):
    @ex.retry(2)
    def fetch():
        """Fetch it."""
        return 1

    assert (fetch.__name__, fetch.__doc__, fetch()) == ("fetch", "Fetch it.", 1)


# --- command -----------------------------------------------------------------

def test_command_without_brackets(ex):
    def hello():
        return "hi"

    assert ex.command(hello) is hello
    assert ex.COMMANDS == {"hello": hello}


def test_command_with_name(ex):
    @ex.command(name="bye")
    def goodbye():
        return "bye"

    assert goodbye() == "bye"
    assert ex.COMMANDS == {"bye": goodbye}


def test_command_with_empty_brackets(ex):
    @ex.command()
    def status():
        pass

    assert ex.COMMANDS["status"] is status


def test_command_registers_several(ex):
    @ex.command
    def a():
        pass

    @ex.command(name="z")
    def b():
        pass

    assert sorted(ex.COMMANDS) == ["a", "z"]
