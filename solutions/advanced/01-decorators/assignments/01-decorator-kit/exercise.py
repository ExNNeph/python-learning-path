"""Assignment 01 · Decorator kit: template solution."""

import functools

COMMANDS = {}


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1          # the attribute lives on the wrapper, which IS the decorated function
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        # `in` + lookup instead of cache.get(): a cached None or 0 must count as a hit too.
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


def retry(times, *, exceptions=(Exception,)):
    # Validate here, in the outermost level: a wrong decorator fails at import time, not on the first call.
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:     # anything else propagates immediately
                    last_error = error
            raise last_error
        return wrapper
    return decorator


def command(func=None, *, name=None):
    def decorator(f):
        COMMANDS[name or f.__name__] = f
        return f                      # registering, not wrapping: the function stays as it is

    if func is None:                  # @command(name=...): we are the factory
        return decorator
    return decorator(func)            # @command: we are the decorator


if __name__ == "__main__":
    @memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    print(fib(90))
