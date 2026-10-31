"""Assignment 09 · Coroutine tools.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/08-generators-in-depth/assignments/09-coroutine-tools -v
"""

import functools


class Reset(Exception):
    """Thrown into accumulator() to set its total back to 0."""


# --- delegation and return values ----------------------------------------------

def flatten(items):
    """Yield the leaves of arbitrarily nested iterables; str and bytes are leaves."""
    raise NotImplementedError


def counted(iterable):
    """Yield every item, then return how many there were."""
    raise NotImplementedError


def chain_with_counts(*iterables):
    """Yield all items of all iterables; return the list of their counts."""
    raise NotImplementedError


# --- coroutines ------------------------------------------------------------------

def primed(func):
    """Decorator: create the generator and advance it to its first yield."""
    raise NotImplementedError


def averager():
    """Primed coroutine: send(number) → running average."""
    raise NotImplementedError


def accumulator():
    """Primed coroutine: send(n) → new total; send(None) → total; throw(Reset) → 0."""
    raise NotImplementedError


# --- a push pipeline ---------------------------------------------------------------

def collect(results):
    """Primed coroutine: append every received value to results."""
    raise NotImplementedError


def grep(pattern, target):
    """Primed coroutine: pass lines containing pattern on to target; close target when closed."""
    raise NotImplementedError


def transform(func, target):
    """Primed coroutine: send func(value) to target; close target when closed."""
    raise NotImplementedError


def broadcast(*targets):
    """Primed coroutine: send every value to all targets; close them all when closed."""
    raise NotImplementedError


if __name__ == "__main__":
    errors = []
    pipeline = grep("ERROR", transform(str.lower, collect(errors)))
    for line in ["ERROR disk full", "INFO started", "ERROR timeout"]:
        pipeline.send(line)
    pipeline.close()
    print(errors)
