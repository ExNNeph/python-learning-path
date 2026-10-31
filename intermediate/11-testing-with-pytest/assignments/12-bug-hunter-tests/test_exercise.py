"""Tests for assignment 12. Run: pytest intermediate/11-testing-with-pytest/assignments/12-bug-hunter-tests -v

Spoiler warning: this file contains the mutants your checks must catch.
Try the assignment first, and read the failure messages instead of this file.
"""

import re

import pytest


def make_slugify(lower=True, runs=True, digits=True, strip_ends=True, strip_after_cut=True, cut_offset=0, validate=True):
    def slugify(text, max_length=40):
        if validate and max_length < 1:
            raise ValueError("max_length must be at least 1")
        pattern = ("[^a-z0-9]" if digits else "[^a-z]") + ("+" if runs else "")
        slug = re.sub(pattern, "-", text.lower() if lower else text)
        if strip_ends:
            slug = slug.strip("-")
        slug = slug[:max(0, max_length + cut_offset)]
        return slug.rstrip("-") if strip_after_cut else slug
    return slugify


SLUGIFY_MUTANTS = {
    "does not lower-case the text": make_slugify(lower=False),
    "turns every separator character into its own dash": make_slugify(runs=False),
    "drops digits": make_slugify(digits=False),
    "keeps dashes at the start and end": make_slugify(strip_ends=False),
    "keeps a dash left at the end by the cut": make_slugify(strip_after_cut=False),
    "cuts one character too early": make_slugify(cut_offset=-1),
    "cuts one character too late": make_slugify(cut_offset=1),
    "accepts max_length < 1": make_slugify(validate=False),
}


def make_parse_duration(minute=60, hour=3600, allow_empty=False, search=False, only_first=False, any_order=False):
    unit = r"\s*(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?\s*"

    def parse_duration(text):
        if any_order:
            parts = dict((u, int(n)) for n, u in re.findall(r"(\d+)([hms])", text))
            if not parts or re.sub(r"\s|\d+[hms]", "", text):
                raise ValueError(text)
            return parts.get("h", 0) * hour + parts.get("m", 0) * minute + parts.get("s", 0)
        match = (re.match if search else re.fullmatch)(unit, text)
        if match is None or (not allow_empty and not any(match.groups())):
            raise ValueError(text)
        values = [int(part or 0) for part in match.groups()]
        if only_first:
            first = next((i for i, part in enumerate(match.groups()) if part), None)
            values = [v if i == first else 0 for i, v in enumerate(values)]
        h, m, s = values
        return h * hour + m * minute + s
    return parse_duration


DURATION_MUTANTS = {
    "counts a minute as 100 seconds": make_parse_duration(minute=100),
    "counts an hour as 60 minutes of 100 seconds": make_parse_duration(hour=6000),
    "returns 0 for empty text": make_parse_duration(allow_empty=True),
    "ignores extra text after a valid duration": make_parse_duration(search=True),
    "only uses the first part ('1h30m' -> 3600)": make_parse_duration(only_first=True),
    "accepts the units in any order": make_parse_duration(any_order=True),
}


def make_cart(strict_discount=False, flat_discount=False, replace_quantity=False, silent_remove=False,
              allow_zero_price=False, allow_zero_quantity=False, count_names=False, no_rounding=False):
    class Cart:
        def __init__(self):
            self._items = {}

        def add(self, name, price, quantity=1):
            if price < 0 or (price == 0 and not allow_zero_price):
                raise ValueError("price")
            if quantity < 0 or (quantity == 0 and not allow_zero_quantity):
                raise ValueError("quantity")
            if name in self._items and not replace_quantity:
                self._items[name][1] += quantity
            else:
                self._items[name] = [price, quantity]

        def remove(self, name):
            if silent_remove:
                self._items.pop(name, None)
            else:
                del self._items[name]

        def count(self):
            if count_names:
                return len(self._items)
            return sum(q for _, q in self._items.values())

        def total(self):
            subtotal = sum(p * q for p, q in self._items.values())
            if subtotal > 100 if strict_discount else subtotal >= 100:
                subtotal = subtotal - 10 if flat_discount else subtotal * 0.9
            return subtotal if no_rounding else round(subtotal, 2)
    return Cart


CART_MUTANTS = {
    "gives the discount only ABOVE 100, not at 100": make_cart(strict_discount=True),
    "takes 10 off instead of 10 %": make_cart(flat_discount=True),
    "replaces the quantity when an item is added again": make_cart(replace_quantity=True),
    "ignores removing an unknown item": make_cart(silent_remove=True),
    "accepts a price of 0": make_cart(allow_zero_price=True),
    "accepts a quantity of 0": make_cart(allow_zero_quantity=True),
    "counts names instead of pieces": make_cart(count_names=True),
    "does not round the total": make_cart(no_rounding=True),
}


def is_caught(check, buggy):
    """True if the check fails (raises anything) for the buggy code."""
    try:
        check(buggy)
    except (Exception, pytest.fail.Exception):
        return True
    return False


def test_check_slugify_passes_on_correct_code(ex):
    ex.check_slugify(ex.slugify)


def test_check_parse_duration_passes_on_correct_code(ex):
    ex.check_parse_duration(ex.parse_duration)


def test_check_cart_passes_on_correct_code(ex):
    ex.check_cart(ex.Cart)


@pytest.mark.parametrize("bug", SLUGIFY_MUTANTS)
def test_check_slugify_catches(ex, bug):
    ex.check_slugify(ex.slugify)        # must pass on correct code first
    assert is_caught(ex.check_slugify, SLUGIFY_MUTANTS[bug]), f"not caught: a slugify that {bug}"


@pytest.mark.parametrize("bug", DURATION_MUTANTS)
def test_check_parse_duration_catches(ex, bug):
    ex.check_parse_duration(ex.parse_duration)
    assert is_caught(ex.check_parse_duration, DURATION_MUTANTS[bug]), f"not caught: a parse_duration that {bug}"


@pytest.mark.parametrize("bug", CART_MUTANTS)
def test_check_cart_catches(ex, bug):
    ex.check_cart(ex.Cart)
    assert is_caught(ex.check_cart, CART_MUTANTS[bug]), f"not caught: a Cart that {bug}"


def test_mutant_factories_without_bugs_are_correct(ex):
    """Sanity check of this grader: the factories without a bug behave like the real code."""
    ex.slugify("x")  # the code under test is importable
    for text in ["Hello World", "  a--b  ", "Python 3!", "x" * 60]:
        for n in (1, 5, 40):
            assert make_slugify()(text, n) == ex.slugify(text, n)
    for text in ["1h30m", "45s", "2h 5m 3s", "90m"]:
        assert make_parse_duration()(text) == ex.parse_duration(text)
