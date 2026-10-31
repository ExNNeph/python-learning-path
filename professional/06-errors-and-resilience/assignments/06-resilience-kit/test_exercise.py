"""Tests for assignment 06. Run: pytest professional/06-errors-and-resilience/assignments/06-resilience-kit -v"""

import random

import pytest


class Script:
    """A fake dependency: each call takes the next outcome; exceptions are raised."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class RateLimited(ConnectionError):
    def __init__(self, retry_after):
        super().__init__("429 Too Many Requests")
        self.retry_after = retry_after


# --- backoff_delays ------------------------------------------------------------

def test_backoff_defaults(ex):
    assert ex.backoff_delays(1) == []
    assert ex.backoff_delays(4) == pytest.approx([0.1, 0.2, 0.4])


def test_backoff_is_capped(ex):
    assert ex.backoff_delays(8, maximum=2.0) == pytest.approx([0.1, 0.2, 0.4, 0.8, 1.6, 2.0, 2.0])


def test_backoff_custom_base_and_factor(ex):
    assert ex.backoff_delays(4, base=1, factor=3, maximum=100) == [1, 3, 9]


def test_backoff_full_jitter(ex):
    expected_rng = random.Random(7)
    expected = [expected_rng.uniform(0, d) for d in [0.1, 0.2, 0.4, 0.8]]
    assert ex.backoff_delays(5, rng=random.Random(7)) == pytest.approx(expected)


def test_backoff_jitter_stays_within_bounds(ex):
    delays = ex.backoff_delays(12, maximum=1.0, rng=random.Random(1))
    caps = [min(1.0, 0.1 * 2**i) for i in range(11)]
    assert all(0 <= d <= cap for d, cap in zip(delays, caps))
    assert delays != caps


def test_backoff_rejects_zero_attempts(ex):
    with pytest.raises(ValueError):
        ex.backoff_delays(0)


# --- retry_call ----------------------------------------------------------------

def test_retry_succeeds_first_time(ex):
    sleeps = []
    assert ex.retry_call(Script("ok"), sleep=sleeps.append) == "ok"
    assert sleeps == []


def test_retry_after_transient_errors(ex):
    func, sleeps = Script(ConnectionError("reset"), TimeoutError("slow"), "ok"), []
    assert ex.retry_call(func, sleep=sleeps.append) == "ok"
    assert func.calls == 3
    assert sleeps == pytest.approx([0.1, 0.2])


def test_retry_gives_up(ex):
    last = TimeoutError("still slow")
    func, sleeps = Script(ConnectionError("a"), ConnectionError("b"), ConnectionError("c"), last), []
    with pytest.raises(ex.RetryError) as info:
        ex.retry_call(func, attempts=4, base=1, factor=2, sleep=sleeps.append)
    error = info.value
    assert func.calls == 4
    assert sleeps == [1, 2, 4]
    assert (error.attempts, error.last) == (4, last)
    assert error.__cause__ is last
    assert str(error) == "gave up after 4 attempts: TimeoutError('still slow')"


def test_retry_does_not_retry_permanent_errors(ex):
    func, sleeps = Script(ValueError("bad input"), "never"), []
    with pytest.raises(ValueError, match="bad input"):
        ex.retry_call(func, sleep=sleeps.append)
    assert (func.calls, sleeps) == (1, [])


def test_retry_custom_retry_on(ex):
    func = Script(KeyError("x"), "ok")
    assert ex.retry_call(func, retry_on=(KeyError,), sleep=lambda s: None) == "ok"
    with pytest.raises(ConnectionError):
        ex.retry_call(Script(ConnectionError()), retry_on=(KeyError,), sleep=lambda s: None)


def test_retry_respects_retry_after(ex):
    func, sleeps = Script(RateLimited(3.5), ConnectionError(), RateLimited(None), "ok"), []
    assert ex.retry_call(func, attempts=4, sleep=sleeps.append) == "ok"
    assert sleeps == pytest.approx([3.5, 0.2, 0.4])


def test_retry_with_jitter(ex):
    rng = random.Random(3)
    expected = ex.backoff_delays(3, rng=random.Random(3))
    sleeps = []
    ex.retry_call(Script(ConnectionError(), ConnectionError(), "ok"), sleep=sleeps.append, rng=rng)
    assert sleeps == pytest.approx(expected)


def test_retry_single_attempt(ex):
    with pytest.raises(ex.RetryError):
        ex.retry_call(Script(ConnectionError()), attempts=1, sleep=lambda s: pytest.fail("no sleep"))


# --- CircuitBreaker ------------------------------------------------------------

def test_breaker_starts_closed_and_passes_calls(ex):
    breaker = ex.CircuitBreaker()
    assert breaker.state == "closed"
    assert breaker.call(lambda a, b=0: a + b, 2, b=3) == 5


def test_breaker_opens_after_threshold(ex):
    clock = FakeClock()
    breaker = ex.CircuitBreaker(failure_threshold=3, reset_timeout=30, clock=clock)
    func = Script(ConnectionError(), ConnectionError(), ConnectionError(), "never")
    for _ in range(2):
        with pytest.raises(ConnectionError):
            breaker.call(func)
        assert breaker.state == "closed"
    with pytest.raises(ConnectionError):
        breaker.call(func)
    assert breaker.state == "open"
    with pytest.raises(ex.CircuitOpenError):
        breaker.call(func)
    assert func.calls == 3                     # failing fast: the dependency was not called again


def test_breaker_counts_only_consecutive_failures(ex):
    breaker = ex.CircuitBreaker(failure_threshold=2, clock=FakeClock())
    func = Script(ConnectionError(), "ok", ConnectionError(), "ok", ConnectionError())
    for _ in range(5):
        try:
            breaker.call(func)
        except ConnectionError:
            pass
    assert breaker.state == "closed"


def test_breaker_half_open_then_closed(ex):
    clock = FakeClock()
    breaker = ex.CircuitBreaker(failure_threshold=1, reset_timeout=30, clock=clock)
    with pytest.raises(ConnectionError):
        breaker.call(Script(ConnectionError()))
    clock.now += 29.9
    assert breaker.state == "open"
    clock.now += 0.1
    assert breaker.state == "half_open"
    assert breaker.call(Script("recovered")) == "recovered"
    assert breaker.state == "closed"


def test_breaker_half_open_failure_reopens_and_restarts_timer(ex):
    clock = FakeClock()
    breaker = ex.CircuitBreaker(failure_threshold=3, reset_timeout=10, clock=clock)
    failing = Script(*[ConnectionError()] * 4)
    for _ in range(3):
        with pytest.raises(ConnectionError):
            breaker.call(failing)
    clock.now += 10
    assert breaker.state == "half_open"
    with pytest.raises(ConnectionError):
        breaker.call(failing)                  # one failed trial is enough to open again
    assert breaker.state == "open"
    clock.now += 9
    assert breaker.state == "open"             # the timer restarted at the trial
    clock.now += 1
    assert breaker.state == "half_open"


def test_breaker_success_after_reopen_resets_count(ex):
    clock = FakeClock()
    breaker = ex.CircuitBreaker(failure_threshold=2, reset_timeout=5, clock=clock)
    func = Script(ConnectionError(), ConnectionError(), "ok", ConnectionError(), "ok")
    for _ in range(2):
        with pytest.raises(ConnectionError):
            breaker.call(func)
    clock.now += 5
    breaker.call(func)
    with pytest.raises(ConnectionError):
        breaker.call(func)
    assert breaker.state == "closed"           # one failure after recovery is below the threshold
    assert breaker.call(func) == "ok"


def test_breaker_default_clock(ex):
    breaker = ex.CircuitBreaker(failure_threshold=1, reset_timeout=60)
    with pytest.raises(ZeroDivisionError):
        breaker.call(lambda: 1 / 0)
    assert breaker.state == "open"


# --- translate -----------------------------------------------------------------

class NotFound(Exception):
    pass


class Unavailable(Exception):
    pass


def test_translate_chains(ex):
    with pytest.raises(NotFound) as info:
        with ex.translate({KeyError: NotFound, OSError: Unavailable}):
            {}["user-42"]
    assert str(info.value) == "'user-42'"
    assert isinstance(info.value.__cause__, KeyError)


def test_translate_matches_subclasses_first_key_wins(ex):
    with pytest.raises(Unavailable) as info:
        with ex.translate({ConnectionError: Unavailable, OSError: NotFound}):
            raise ConnectionRefusedError("refused")
    assert str(info.value) == "refused"
    assert isinstance(info.value.__cause__, ConnectionRefusedError)


def test_translate_passes_other_errors_and_results(ex):
    with pytest.raises(ValueError):
        with ex.translate({KeyError: NotFound}):
            raise ValueError("other")
    with ex.translate({KeyError: NotFound}):
        value = 42
    assert value == 42


def test_translate_as_decorator(ex):
    @ex.translate({ZeroDivisionError: ArithmeticError})
    def ratio(a, b):
        return a / b

    assert ratio(6, 3) == 2
    with pytest.raises(ArithmeticError):
        ratio(1, 0)


# --- idempotent ----------------------------------------------------------------

def test_idempotent_runs_once_per_key(ex):
    store, charges = {}, []

    @ex.idempotent(store)
    def charge(account, cents, *, currency="EUR"):
        charges.append((account, cents, currency))
        return f"receipt-{len(charges)}"

    assert charge("ada", 500, idempotency_key="k1") == "receipt-1"
    assert charge("ada", 500, idempotency_key="k1") == "receipt-1"
    assert charge("ada", 500, idempotency_key="k2") == "receipt-2"
    assert charge("bob", 100, currency="USD", idempotency_key="k3") == "receipt-3"
    assert charges == [("ada", 500, "EUR"), ("ada", 500, "EUR"), ("bob", 100, "USD")]
    assert set(store) == {"k1", "k2", "k3"}
    assert charge.__name__ == "charge"


def test_idempotent_key_reused_with_other_arguments(ex):
    @ex.idempotent({})
    def charge(account, cents):
        return "ok"

    charge("ada", 500, idempotency_key="k1")
    with pytest.raises(ValueError, match="k1"):
        charge("ada", 900, idempotency_key="k1")


def test_idempotent_failures_are_not_stored(ex):
    store = {}
    func = Script(ConnectionError("lost"), "done")

    @ex.idempotent(store)
    def send(message):
        return func()

    with pytest.raises(ConnectionError):
        send("hi", idempotency_key="m1")
    assert store == {} or "m1" not in store
    assert send("hi", idempotency_key="m1") == "done"
    assert send("hi", idempotency_key="m1") == "done"
    assert func.calls == 2


def test_idempotent_requires_the_key(ex):
    @ex.idempotent({})
    def noop():
        return None

    with pytest.raises(TypeError):
        noop()
