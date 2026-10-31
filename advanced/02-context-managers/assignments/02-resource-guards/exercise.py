"""Assignment 02 · Resource guards.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/02-context-managers/assignments/02-resource-guards -v
"""

import copy
import os
import time
from contextlib import ExitStack, contextmanager


class Timer:
    """with Timer() as t: ...  →  t.elapsed is the duration of the block in seconds."""

    def __init__(self, clock=time.perf_counter):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


class Suppress:
    """Swallow the given exception types; the caught exception is stored in .error."""

    def __init__(self, *exceptions):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


@contextmanager
def temp_env(**variables):
    """Set (or, for None, remove) environment variables for the block, then restore them."""
    raise NotImplementedError
    yield  # keeps this a generator until you write your own yield


@contextmanager
def transaction(data):
    """Yield a deep copy of data; copy it back into data only if the block succeeds."""
    raise NotImplementedError
    yield


@contextmanager
def open_all(paths, mode="r"):
    """Open all files, yield the list of file objects, close them all afterwards."""
    raise NotImplementedError
    yield


if __name__ == "__main__":
    with Timer() as t:
        total = sum(range(5_000_000))
    print(f"summed to {total} in {t.elapsed:.3f} s")
