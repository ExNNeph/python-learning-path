"""Assignment 02 · Function toolkit.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest intermediate/02-functions-in-depth/assignments/02-function-toolkit -v
"""


def format_price(amount, /, *, currency="EUR", decimals=2):
    """Return the amount with `decimals` decimals and the currency, e.g. '12.50 EUR'."""
    raise NotImplementedError


def calculate(a, operator, b):
    """Apply '+', '-', '*' or '/' using a dispatch dict.

    Raise ValueError("unknown operator: '<operator>'") for anything else.
    """
    raise NotImplementedError


def pipeline(*functions):
    """Return one function that applies all functions, left to right."""
    raise NotImplementedError


def make_multiplier(factor):
    """Return a function that multiplies its argument by factor."""
    raise NotImplementedError


def make_counter(start=0, step=1):
    """Return a function that returns start, start + step, ... on successive calls."""
    raise NotImplementedError


def call_counted(func):
    """Return (wrapper, calls).

    wrapper forwards all positional and keyword arguments to func and returns its result.
    calls() returns how many times wrapper has been called so far.
    """
    raise NotImplementedError


if __name__ == "__main__":
    slugify = pipeline(str.strip, str.lower, lambda s: s.replace(" ", "-"))
    print(slugify("  Functions In Depth  "))
    print(format_price(calculate(19.99, "*", 3), currency="EUR"))
