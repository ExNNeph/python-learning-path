"""Price calculation for a small web shop. All amounts are in cents.

This is the module under test. It is correct: do not change it.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str
    unit_price: int
    quantity: int = 1


def subtotal(items):
    """Sum of unit_price * quantity. A quantity below 1 raises ValueError."""
    for item in items:
        if item.quantity < 1:
            raise ValueError(f"invalid quantity for {item.name}: {item.quantity}")
    return sum(item.unit_price * item.quantity for item in items)


def discount(amount, code):
    """The discount in cents for a discount code (case-insensitive).

    None      -> 0
    "SAVE10"  -> 10 % of the amount, rounded down
    "FLAT5"   -> 500, but only for amounts of at least 2000 (otherwise 0)
    other     -> ValueError
    """
    if code is None:
        return 0
    code = code.upper()
    if code == "SAVE10":
        return amount // 10
    if code == "FLAT5":
        return 500 if amount >= 2000 else 0
    raise ValueError(f"unknown discount code: {code}")


def shipping(amount):
    """Free shipping from 5000 cents on, 495 cents below."""
    return 0 if amount >= 5000 else 495


def convert(cents, currency, rates):
    """Convert euro cents to `currency`. "EUR" needs no rate lookup.

    `rates` is any object with a method get_rate(currency) -> float.
    The result is rounded to whole cents.
    """
    if currency == "EUR":
        return cents
    return round(cents * rates.get_rate(currency))


def total(items, code=None, currency="EUR", rates=None):
    """subtotal - discount + shipping (on the discounted amount), converted to `currency`."""
    amount = subtotal(items)
    amount -= discount(amount, code)
    return convert(amount + shipping(amount), currency, rates)
