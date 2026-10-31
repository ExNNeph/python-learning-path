"""Assignment 09 · Coroutine tools: template solution."""

import functools


class Reset(Exception):
    """Thrown into accumulator() to set its total back to 0."""


# --- delegation and return values ----------------------------------------------

def flatten(items):
    for item in items:
        if isinstance(item, (str, bytes)):
            yield item                      # iterable, but a leaf for us (and "a" would recurse forever)
            continue
        try:
            iter(item)
        except TypeError:
            yield item                      # not iterable: a leaf
        else:
            yield from flatten(item)


def counted(iterable):
    count = 0
    for item in iterable:
        yield item
        count += 1
    return count                            # travels in StopIteration.value


def chain_with_counts(*iterables):
    counts = []
    for iterable in iterables:
        counts.append((yield from counted(iterable)))   # yield from evaluates to the return value
    return counts


# --- coroutines ------------------------------------------------------------------

def primed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)                           # run to the first yield, so send() works right away
        return gen
    return wrapper


@primed
def averager():
    total = count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


@primed
def accumulator():
    total = 0
    while True:
        try:
            value = yield total
        except Reset:                       # throw(Reset) raises right here, at the paused yield
            total = 0
            continue
        if value is not None:
            total += value


# --- a push pipeline ---------------------------------------------------------------

@primed
def collect(results):
    while True:
        results.append((yield))


@primed
def grep(pattern, target):
    try:
        while True:
            line = yield
            if pattern in line:
                target.send(line)
    finally:
        target.close()                      # GeneratorExit (close) lands here: pass it down the line


@primed
def transform(func, target):
    try:
        while True:
            target.send(func((yield)))
    finally:
        target.close()


@primed
def broadcast(*targets):
    try:
        while True:
            value = yield
            for target in targets:
                target.send(value)
    finally:
        for target in targets:
            target.close()


if __name__ == "__main__":
    errors = []
    pipeline = grep("ERROR", transform(str.lower, collect(errors)))
    for line in ["ERROR disk full", "INFO started", "ERROR timeout"]:
        pipeline.send(line)
    pipeline.close()
    print(errors)
