"""Assignment 05 · Inventory.

Turn the classes below into an Enum and dataclasses, and replace each
`raise NotImplementedError` with your code.
Check your work:  pytest intermediate/05-dataclasses-and-enums/assignments/05-inventory -v
"""

from dataclasses import dataclass, field
from enum import Enum


class Category:
    """TODO: an Enum with FOOD = "food", TOOLS = "tools", TOYS = "toys"."""


class Location:
    """TODO: a frozen, ordered dataclass with the fields aisle (str) and shelf (int)."""


class Item:
    """TODO: a dataclass with name, price, quantity=0, category=Category.FOOD,
    location=Location("A", 1) and tags (a fresh list for every item).
    """

    def __post_init__(self):
        """Normalise the name, convert a string category, validate the numbers."""
        raise NotImplementedError

    @property
    def total_value(self):
        raise NotImplementedError


class Inventory:
    def __init__(self):
        raise NotImplementedError

    def add(self, item):
        """Add an item. Raise ValueError if an item with that name exists."""
        raise NotImplementedError

    def get(self, name):
        """Return the item (name matched stripped and case-insensitively). Unknown: KeyError."""
        raise NotImplementedError

    def sell(self, name, quantity):
        """Reduce the quantity and return the price to pay."""
        raise NotImplementedError

    def low_stock(self, threshold=5):
        """Return the sorted names of items with a quantity below threshold."""
        raise NotImplementedError

    def value_by_category(self):
        """Return a dict Category -> total value."""
        raise NotImplementedError

    def by_location(self):
        """Return all items sorted by location, then name."""
        raise NotImplementedError


if __name__ == "__main__":
    shop = Inventory()
    shop.add(Item("apple", 0.5, 10))
    shop.add(Item("hammer", 12.0, 2, "tools", Location("C", 1)))
    shop.add(Item("yo-yo", 3.5, 7, Category.TOYS, Location("B", 4)))
    print("Sold apples for", shop.sell("Apple", 4))
    print("Low stock:", shop.low_stock())
    for item in shop.by_location():
        print(f"{item.location.aisle}{item.location.shelf}  {item.name:<8} {item.quantity:>3}")
