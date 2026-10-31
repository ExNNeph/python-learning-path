"""Assignment 06 · Resilience kit: template solution."""

import functools
import time
from contextlib import contextmanager

TRANSIENT = (ConnectionError, TimeoutError)


def backoff_delays(attempts, *, base=0.1, factor=2.0, maximum=5.0, rng=None):
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    delays = [min(maximum, base * factor**i) for i in range(attempts - 1)]
    if rng is not None:
        # "Full jitter": anywhere between 0 and the backoff, so clients spread out.
        delays = [rng.uniform(0, delay) for delay in delays]
    return delays


class RetryError(Exception):
    def __init__(self, attempts, last):
        super().__init__(f"gave up after {attempts} attempts: {last!r}")
        self.attempts = attempts
        self.last = last


def retry_call(func, *, attempts=3, retry_on=TRANSIENT, base=0.1, factor=2.0, maximum=5.0,
               sleep=time.sleep, rng=None):
    delays = backoff_delays(attempts, base=base, factor=factor, maximum=maximum, rng=rng)
    for attempt in range(attempts):
        try:
            return func()
        except retry_on as error:
            if attempt == attempts - 1:
                raise RetryError(attempts, error) from error
            # A server that says how long to wait (HTTP Retry-After) knows better than our formula.
            retry_after = getattr(error, "retry_after", None)
            sleep(retry_after if retry_after is not None else delays[attempt])
        # Any other exception is permanent: it propagates on the first attempt.


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=30.0, clock=time.monotonic):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.clock = clock
        self.failures = 0
        self.opened_at = None              # None: closed

    @property
    def state(self):
        if self.opened_at is None:
            return "closed"
        if self.clock() - self.opened_at >= self.reset_timeout:
            return "half_open"
        return "open"

    def call(self, func, *args, **kwargs):
        state = self.state
        if state == "open":
            raise CircuitOpenError("circuit open: failing fast")
        try:
            result = func(*args, **kwargs)
        except Exception:
            self.failures += 1
            if state == "half_open" or self.failures >= self.failure_threshold:
                self.opened_at = self.clock()      # (re)open and restart the timer
            raise
        self.failures = 0
        self.opened_at = None                      # a success closes the circuit
        return result


@contextmanager
def translate(mapping):
    try:
        yield
    except tuple(mapping) as error:
        for source, target in mapping.items():     # the first matching entry wins
            if isinstance(error, source):
                raise target(str(error)) from error


def idempotent(store):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, idempotency_key, **kwargs):
            call = (args, kwargs)
            if idempotency_key in store:
                previous_call, result = store[idempotency_key]
                if previous_call != call:
                    raise ValueError(f"idempotency key {idempotency_key!r} reused with different arguments")
                return result                      # the operation already happened: do not repeat it
            result = func(*args, **kwargs)
            store[idempotency_key] = (call, result)  # only successes are stored, so a failure can be retried
            return result
        return wrapper
    return decorator


if __name__ == "__main__":
    import random

    print(backoff_delays(8, maximum=2.0))
    print([round(d, 3) for d in backoff_delays(5, rng=random.Random(42))])

    calls = iter([ConnectionError("reset"), TimeoutError("slow"), "ok"])

    def flaky():
        outcome = next(calls)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    print(retry_call(flaky, sleep=lambda s: print(f"  sleeping {s:.2f} s")))
