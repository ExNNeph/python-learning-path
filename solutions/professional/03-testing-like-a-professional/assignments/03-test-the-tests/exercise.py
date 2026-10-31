"""Assignment 03 · Test the tests: template solution.

Every test is named after one behaviour, and the cases sit at the boundaries,
because that is where the planted bugs (and most real ones) live.
"""

from unittest.mock import Mock

import pytest

from pricing import Item, convert, discount, shipping, subtotal, total


@pytest.fixture
def rates():
    """A mock rate provider: a stub (fixed answer) we can also inspect like a spy."""
    provider = Mock()
    provider.get_rate.return_value = 1.25
    return provider


# --- subtotal ------------------------------------------------------------------

def test_subtotal_multiplies_by_quantity():
    assert subtotal([Item("pen", 150, quantity=3), Item("book", 2000)]) == 2450


def test_subtotal_of_nothing_is_zero():
    assert subtotal([]) == 0


@pytest.mark.parametrize("quantity", [0, -1])
def test_subtotal_rejects_quantity_below_one(quantity):
    with pytest.raises(ValueError, match="invalid quantity for pen"):
        subtotal([Item("pen", 150, quantity=quantity)])


# --- discount ------------------------------------------------------------------

def test_no_code_no_discount():
    assert discount(3000, None) == 0


@pytest.mark.parametrize("amount, expected", [(2000, 200), (1999, 199), (9, 0)], ids=["even", "rounds-down", "tiny"])
def test_save10_is_ten_percent_rounded_down(amount, expected):
    assert discount(amount, "SAVE10") == expected


@pytest.mark.parametrize("amount, expected", [(1999, 0), (2000, 500), (8000, 500)], ids=["below", "exactly", "above"])
def test_flat5_needs_a_minimum_of_2000(amount, expected):
    assert discount(amount, "FLAT5") == expected


@pytest.mark.parametrize("code", ["save10", "Save10", "SAVE10"])
def test_codes_are_case_insensitive(code):
    assert discount(1000, code) == 100


def test_unknown_code_raises():
    with pytest.raises(ValueError, match="unknown discount code"):
        discount(1000, "FREE")


# --- shipping ------------------------------------------------------------------

@pytest.mark.parametrize("amount, expected", [(0, 495), (4999, 495), (5000, 0), (12_000, 0)],
                         ids=["empty", "just-below", "exactly", "far-above"])
def test_shipping_is_free_from_5000(amount, expected):
    assert shipping(amount) == expected


# --- convert -------------------------------------------------------------------

def test_euro_needs_no_rate_lookup(rates):
    assert convert(1000, "EUR", rates) == 1000
    rates.get_rate.assert_not_called()          # only a mock (spy) can see this


def test_euro_works_without_a_rate_provider():
    assert convert(1000, "EUR", None) == 1000


def test_other_currencies_look_up_their_rate(rates):
    assert convert(1000, "USD", rates) == 1250
    rates.get_rate.assert_called_once_with("USD")


def test_convert_rounds_to_whole_cents(rates):
    rates.get_rate.return_value = 1.0006
    assert convert(1000, "USD", rates) == 1001  # 1000.6 rounds up, not down


# --- total ---------------------------------------------------------------------

def test_total_without_code_adds_shipping():
    assert total([Item("book", 2000)]) == 2495


def test_total_shipping_is_based_on_the_discounted_amount():
    # 5000 qualifies for free shipping, but after SAVE10 it is 4500, which does not.
    assert total([Item("lamp", 5000)], code="SAVE10") == 4500 + 495


def test_total_converts_the_final_amount(rates):
    assert total([Item("book", 2000)], code="FLAT5", currency="USD", rates=rates) == round((1500 + 495) * 1.25)
    rates.get_rate.assert_called_once_with("USD")
