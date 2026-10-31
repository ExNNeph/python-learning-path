"""Assignment 02 · Resource guards: template solution."""

import copy
import os
import time
from contextlib import ExitStack, contextmanager


class Timer:
    def __init__(self, clock=time.perf_counter):
        self.clock = clock               # injectable, so tests do not depend on real time
        self.elapsed = None

    def __enter__(self):
        self.start = self.clock()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = self.clock() - self.start
        return False                     # measure, never swallow


class Suppress:
    def __init__(self, *exceptions):
        self.exceptions = exceptions
        self.error = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None and issubclass(exc_type, self.exceptions):
            self.error = exc
            return True                  # handled: continue after the with block
        return False


def _apply(values):
    for name, value in values.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


@contextmanager
def temp_env(**variables):
    # Restoring is the same operation as setting, with the old values (None = was not there).
    old = {name: os.environ.get(name) for name in variables}
    _apply(variables)
    try:
        yield
    finally:
        _apply(old)


@contextmanager
def transaction(data):
    draft = copy.deepcopy(data)          # deep: nested lists must not leak into data
    yield draft
    # Only reached if the block did not raise: @contextmanager re-raises at the yield.
    data.clear()
    data.update(draft)                   # same dict object, so every reference sees the commit


@contextmanager
def open_all(paths, mode="r"):
    with ExitStack() as stack:
        yield [stack.enter_context(open(path, mode)) for path in paths]


if __name__ == "__main__":
    with Timer() as t:
        total = sum(range(5_000_000))
    print(f"summed to {total} in {t.elapsed:.3f} s")
