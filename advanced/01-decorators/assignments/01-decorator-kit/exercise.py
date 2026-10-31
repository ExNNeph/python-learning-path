"""Assignment 01 · Decorator kit.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/01-decorators/assignments/01-decorator-kit -v
"""

import functools

COMMANDS = {}


def count_calls(func):
    """Count the calls of func in the attribute `calls` of the returned wrapper."""
    raise NotImplementedError


def memoize(func):
    """Cache results by positional arguments; expose `cache` (dict) and `cache_clear()`."""
    raise NotImplementedError


def retry(times, *, exceptions=(Exception,)):
    """Call the function up to `times` times while it raises one of `exceptions`.

    Re-raise the last exception if every attempt fails. times < 1: ValueError.
    """
    raise NotImplementedError


def command(func=None, *, name=None):
    """Register func in COMMANDS under `name` (default: func.__name__) and return it unchanged.

    Works as @command and as @command(name="...").
    """
    raise NotImplementedError


if __name__ == "__main__":
    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print(fib(90))
