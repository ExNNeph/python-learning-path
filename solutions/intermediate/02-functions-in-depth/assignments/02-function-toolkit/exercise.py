"""Assignment 02 · Function toolkit: template solution."""

# A dispatch table: operator symbol -> function. Defined once at module level, because it
# never changes. Adding an operator is one new line, not one more elif branch.
OPERATIONS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


def format_price(amount, /, *, currency="EUR", decimals=2):
    """Return the amount with `decimals` decimals and the currency, e.g. '12.50 EUR'."""
    # The format spec itself can contain a replacement field: {decimals} is filled in first.
    return f"{amount:.{decimals}f} {currency}"


def calculate(a, operator, b):
    """Apply '+', '-', '*' or '/' using a dispatch dict."""
    try:
        operation = OPERATIONS[operator]
    except KeyError:
        # `from None` hides the internal KeyError: the caller only needs our message.
        raise ValueError(f"unknown operator: '{operator}'") from None
    # Kept outside the try, so a ZeroDivisionError from "/" is not mistaken for a bad operator.
    return operation(a, b)


def pipeline(*functions):
    """Return one function that applies all functions, left to right."""
    def run(value):
        for func in functions:          # `functions` is captured by the closure
            value = func(value)
        return value                    # no functions: the loop does nothing
    return run


def make_multiplier(factor):
    """Return a function that multiplies its argument by factor."""
    def multiply(number):
        return number * factor
    return multiply


def make_counter(start=0, step=1):
    """Return a function that returns start, start + step, ... on successive calls."""
    current = start

    def counter():
        nonlocal current                # we reassign it, so it must not become a new local
        value = current
        current += step
        return value
    return counter


def call_counted(func):
    """Return (wrapper, calls)."""
    count = 0

    def wrapper(*args, **kwargs):
        nonlocal count
        count += 1
        return func(*args, **kwargs)    # forward everything, keyword arguments included

    def calls():
        return count                    # only reads: no nonlocal needed

    # Both inner functions close over the SAME `count` variable.
    return wrapper, calls


if __name__ == "__main__":
    slugify = pipeline(str.strip, str.lower, lambda s: s.replace(" ", "-"))
    print(slugify("  Functions In Depth  "))
    print(format_price(calculate(19.99, "*", 3), currency="EUR"))
