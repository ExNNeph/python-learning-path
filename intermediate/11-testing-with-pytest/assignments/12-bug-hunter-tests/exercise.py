"""Assignment 12 · Bug hunter tests.

The code below is correct. Write the three check functions at the bottom so that they
pass for this code and fail for every buggy version (mutant) the grader tries.
Check your work:  pytest intermediate/11-testing-with-pytest/assignments/12-bug-hunter-tests -v
"""

import re

import pytest


# ---------------------------------------------------------------------------
# The code under test. It is correct: do not change it.
# ---------------------------------------------------------------------------

def slugify(text, max_length=40):
    """Turn a title into a URL part: 'Hello, World!' -> 'hello-world'."""
    if max_length < 1:
        raise ValueError("max_length must be at least 1")
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:max_length].rstrip("-")


DURATION = re.compile(r"\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?\s*")


def parse_duration(text):
    """Return the seconds in a text like '1h30m', '45s' or '2h 5m 3s'."""
    match = DURATION.fullmatch(text)
    if match is None or not any(match.groups()):
        raise ValueError(f"invalid duration: {text!r}")
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds


class Cart:
    """A shopping cart with 10 % off from a sum of 100.00."""

    DISCOUNT_FROM = 100.0
    DISCOUNT_RATE = 0.10

    def __init__(self):
        self._items = {}                    # name -> [price, quantity]

    def add(self, name, price, quantity=1):
        if price <= 0:
            raise ValueError("price must be positive")
        if quantity < 1:
            raise ValueError("quantity must be at least 1")
        if name in self._items:
            self._items[name][1] += quantity
        else:
            self._items[name] = [price, quantity]

    def remove(self, name):
        del self._items[name]               # KeyError for unknown names

    def count(self):
        return sum(quantity for _, quantity in self._items.values())

    def total(self):
        subtotal = sum(price * quantity for price, quantity in self._items.values())
        if subtotal >= self.DISCOUNT_FROM:
            subtotal *= 1 - self.DISCOUNT_RATE
        return round(subtotal, 2)


# ---------------------------------------------------------------------------
# YOUR TESTS. Always use the parameter (slugify, parse_duration, Cart), never the
# module-level names above.
# ---------------------------------------------------------------------------

def check_slugify(slugify):
    """Assert everything the specification says about slugify."""
    raise NotImplementedError


def check_parse_duration(parse_duration):
    """Assert everything the specification says about parse_duration."""
    raise NotImplementedError


def check_cart(Cart):
    """Create fresh carts with Cart() and assert everything the specification says."""
    raise NotImplementedError


if __name__ == "__main__":
    for check, target in [(check_slugify, slugify), (check_parse_duration, parse_duration), (check_cart, Cart)]:
        check(target)
        print(f"{check.__name__}: passed on the correct code")
