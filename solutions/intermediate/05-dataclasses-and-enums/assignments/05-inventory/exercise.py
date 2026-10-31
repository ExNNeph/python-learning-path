"""Assignment 05 · Inventory: template solution."""

from dataclasses import dataclass, field
from enum import Enum


class Category(Enum):
    FOOD = "food"
    TOOLS = "tools"
    TOYS = "toys"


# frozen: a location is a value, it never changes (and it can safely be a default).
# order: generated comparisons compare (aisle, shelf) as a tuple, in field order.
@dataclass(frozen=True, order=True)
class Location:
    aisle: str
    shelf: int


def normalise(name):
    """The one rule for item names, shared by Item and Inventory."""
    return name.strip().lower()


@dataclass
class Item:
    name: str
    price: float
    quantity: int = 0
    category: Category = Category.FOOD
    location: Location = Location("A", 1)
    # default_factory is called for every new Item, so no two items share one list.
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Normalise the name, convert a string category, validate the numbers."""
        self.name = normalise(self.name)
        if not self.name:
            raise ValueError("name must not be empty")
        if self.price < 0:
            raise ValueError(f"price must not be negative, got {self.price}")
        if self.quantity < 0:
            raise ValueError(f"quantity must not be negative, got {self.quantity}")
        # Convert at the edge: callers may pass "tools" (e.g. read from a file), but inside
        # the program we only ever work with Category members.
        if not isinstance(self.category, Category):
            self.category = Category(self.category)     # ValueError for unknown values

    @property
    def total_value(self):
        return self.price * self.quantity


class Inventory:
    def __init__(self):
        self._items = {}                    # normalised name -> Item

    def add(self, item):
        """Add an item. Raise ValueError if an item with that name exists."""
        if item.name in self._items:
            raise ValueError(f"item already exists: {item.name}")
        self._items[item.name] = item

    def get(self, name):
        """Return the item (name matched stripped and case-insensitively). Unknown: KeyError."""
        return self._items[normalise(name)]

    def sell(self, name, quantity):
        """Reduce the quantity and return the price to pay."""
        item = self.get(name)
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if quantity > item.quantity:
            raise ValueError(f"not enough {item.name} in stock")
        item.quantity -= quantity
        return item.price * quantity

    def low_stock(self, threshold=5):
        """Return the sorted names of items with a quantity below threshold."""
        return sorted(name for name, item in self._items.items() if item.quantity < threshold)

    def value_by_category(self):
        """Return a dict Category -> total value."""
        # Enum members are hashable, so they work as dict keys.
        totals = {}
        for item in self._items.values():
            totals[item.category] = totals.get(item.category, 0) + item.total_value
        return totals

    def by_location(self):
        """Return all items sorted by location, then name."""
        # Location objects compare like (aisle, shelf) tuples thanks to order=True.
        return sorted(self._items.values(), key=lambda item: (item.location, item.name))


if __name__ == "__main__":
    shop = Inventory()
    shop.add(Item("apple", 0.5, 10))
    shop.add(Item("hammer", 12.0, 2, "tools", Location("C", 1)))
    shop.add(Item("yo-yo", 3.5, 7, Category.TOYS, Location("B", 4)))
    print("Sold apples for", shop.sell("Apple", 4))
    print("Low stock:", shop.low_stock())
    for item in shop.by_location():
        print(f"{item.location.aisle}{item.location.shelf}  {item.name:<8} {item.quantity:>3}")
