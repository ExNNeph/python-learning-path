"""Assignment 12 · Bug hunter tests: template solution."""

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
# The tests. Each block of asserts targets one rule of the specification; the comment
# names the bug it is there to catch.
# ---------------------------------------------------------------------------

def check_slugify(slugify):
    """Assert everything the specification says about slugify."""
    # the basic transformation (catches: no lower-casing, wrong separator)
    assert slugify("Hello World") == "hello-world"
    # digits are kept (catches: a pattern like [^a-z]+)
    assert slugify("Python 3 Tips") == "python-3-tips"
    # a RUN of separators becomes ONE dash (catches: [^a-z0-9] without +)
    assert slugify("a  --  b") == "a-b"
    # dashes at both ends are removed (catches: strip only on one side, or not at all)
    assert slugify("  Hello, World!  ") == "hello-world"
    assert slugify("!!!") == ""
    # the cut: exactly max_length characters (catches: off-by-one)
    assert slugify("abcdef", max_length=6) == "abcdef"
    assert slugify("abcdef", max_length=5) == "abcde"
    # a cut right after a dash removes that dash (catches: no rstrip after the cut)
    assert slugify("hello world", max_length=6) == "hello"
    # the default max_length is 40
    assert slugify("a" * 50) == "a" * 40
    # invalid max_length (catches: a missing check)
    with pytest.raises(ValueError):
        slugify("x", max_length=0)
    assert slugify("x", max_length=1) == "x"        # the boundary that is still valid


def check_parse_duration(parse_duration):
    """Assert everything the specification says about parse_duration."""
    # each unit on its own (catches: a wrong multiplier for any unit)
    assert parse_duration("2h") == 7200
    assert parse_duration("5m") == 300
    assert parse_duration("45s") == 45
    # combinations add up (catches: only the first part is used)
    assert parse_duration("1h30m") == 5400
    assert parse_duration("2h 5m 3s") == 7503
    assert parse_duration("1m 1s") == 61
    # multi-digit numbers
    assert parse_duration("90m") == 5400
    # invalid input: empty, nothing but spaces, unknown unit, wrong order, extra text
    for bad in ["", "   ", "10", "5d", "30m1h", "1h junk", "h", "1.5h"]:
        with pytest.raises(ValueError):
            parse_duration(bad)


def check_cart(Cart):
    """Create fresh carts with Cart() and assert everything the specification says."""
    # an empty cart
    cart = Cart()
    assert cart.count() == 0
    assert cart.total() == 0

    # adding, counting and totalling (catches: count = number of names, not pieces)
    cart.add("tea", 3.5, quantity=2)
    cart.add("cake", 2.0)
    assert cart.count() == 3
    assert cart.total() == pytest.approx(9.0)

    # adding the same name again INCREASES the quantity (catches: replacing it)
    cart.add("tea", 3.5)
    assert cart.count() == 4
    assert cart.total() == pytest.approx(12.5)

    # remove deletes the item completely; unknown names raise (catches: silent ignore)
    cart.remove("tea")
    assert cart.count() == 1
    assert cart.total() == pytest.approx(2.0)
    with pytest.raises(KeyError):
        cart.remove("tea")

    # invalid input (catches: missing checks, or checks with < instead of <=)
    for price, quantity in [(0, 1), (-1, 1), (1, 0), (1, -2)]:
        with pytest.raises(ValueError):
            Cart().add("x", price, quantity)

    # the discount boundary (catches: > instead of >=, a flat 10 instead of 10 %)
    below, at, above = Cart(), Cart(), Cart()
    below.add("item", 99.99)
    at.add("item", 100.0)
    above.add("item", 50.0, quantity=4)
    assert below.total() == pytest.approx(99.99)
    assert at.total() == pytest.approx(90.0)
    assert above.total() == pytest.approx(180.0)

    # rounding to 2 decimals
    # (0.1 * 3 is 0.30000000000000004 in floating point, so this exact == needs the rounding)
    rounded = Cart()
    rounded.add("dime", 0.1, quantity=3)
    assert rounded.total() == 0.3


if __name__ == "__main__":
    for check, target in [(check_slugify, slugify), (check_parse_duration, parse_duration), (check_cart, Cart)]:
        check(target)
        print(f"{check.__name__}: passed on the correct code")
