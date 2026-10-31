"""Tests for assignment 05. Run: pytest intermediate/05-dataclasses-and-enums/assignments/05-inventory -v"""

import dataclasses
from enum import Enum

import pytest


def test_category_enum(ex):
    assert issubclass(ex.Category, Enum)
    assert [(c.name, c.value) for c in ex.Category] == [("FOOD", "food"), ("TOOLS", "tools"), ("TOYS", "toys")]


def test_location_is_frozen_dataclass(ex):
    location = ex.Location("A", 1)
    assert dataclasses.is_dataclass(location)
    with pytest.raises(dataclasses.FrozenInstanceError):
        location.shelf = 2


def test_location_equality_and_hash(ex):
    assert ex.Location("A", 1) == ex.Location("A", 1)
    assert len({ex.Location("A", 1), ex.Location("A", 1), ex.Location("B", 1)}) == 2


def test_location_order(ex):
    unsorted = [ex.Location("B", 1), ex.Location("A", 3), ex.Location("A", 2)]
    assert sorted(unsorted) == [ex.Location("A", 2), ex.Location("A", 3), ex.Location("B", 1)]


def test_item_is_dataclass_with_fields_in_order(ex):
    assert dataclasses.is_dataclass(ex.Item)
    names = [f.name for f in dataclasses.fields(ex.Item)]
    assert names == ["name", "price", "quantity", "category", "location", "tags"]


def test_item_defaults(ex):
    item = ex.Item("apple", 0.5)
    assert item.quantity == 0
    assert item.category is ex.Category.FOOD
    assert item.location == ex.Location("A", 1)
    assert item.tags == []


def test_item_tags_are_not_shared(ex):
    first, second = ex.Item("apple", 0.5), ex.Item("pear", 0.7)
    first.tags.append("fruit")
    assert second.tags == []


def test_item_repr(ex):
    assert repr(ex.Item("  Apple ", 0.5, 10)) == (
        "Item(name='apple', price=0.5, quantity=10, category=<Category.FOOD: 'food'>, "
        "location=Location(aisle='A', shelf=1), tags=[])"
    )


def test_item_equality(ex):
    assert ex.Item("Apple", 0.5, 1) == ex.Item("apple ", 0.5, 1)
    assert ex.Item("apple", 0.5, 1) != ex.Item("apple", 0.5, 2)


def test_item_category_from_string(ex):
    assert ex.Item("hammer", 12.0, category="tools").category is ex.Category.TOOLS


def test_item_invalid_category(ex):
    with pytest.raises(ValueError):
        ex.Item("hammer", 12.0, category="weapons")


@pytest.mark.parametrize("args", [("  ", 1.0), ("apple", -0.01), ("apple", 1.0, -1)])
def test_item_validation(ex, args):
    with pytest.raises(ValueError):
        ex.Item(*args)


def test_item_total_value(ex):
    assert ex.Item("apple", 0.5, 10).total_value == 5.0


@pytest.fixture
def shop(ex):
    inventory = ex.Inventory()
    inventory.add(ex.Item("apple", 0.5, 10))
    inventory.add(ex.Item("hammer", 12.0, 2, "tools", ex.Location("C", 1)))
    inventory.add(ex.Item("yo-yo", 3.5, 7, ex.Category.TOYS, ex.Location("B", 4)))
    inventory.add(ex.Item("banana", 0.25, 3, location=ex.Location("B", 4)))
    return inventory


def test_add_duplicate(ex, shop):
    with pytest.raises(ValueError):
        shop.add(ex.Item(" APPLE", 1.0))


def test_get(shop):
    assert shop.get(" Apple ").name == "apple"
    with pytest.raises(KeyError):
        shop.get("pear")


def test_sell(shop):
    assert shop.sell("Apple", 4) == 2.0
    assert shop.get("apple").quantity == 6


def test_sell_everything(shop):
    shop.sell("hammer", 2)
    assert shop.get("hammer").quantity == 0


def test_sell_too_many_changes_nothing(shop):
    with pytest.raises(ValueError, match="not enough hammer in stock"):
        shop.sell("hammer", 3)
    assert shop.get("hammer").quantity == 2


@pytest.mark.parametrize("quantity", [0, -1])
def test_sell_needs_positive_quantity(shop, quantity):
    with pytest.raises(ValueError):
        shop.sell("apple", quantity)
    assert shop.get("apple").quantity == 10


def test_sell_unknown(shop):
    with pytest.raises(KeyError):
        shop.sell("pear", 1)


def test_low_stock(shop):
    assert shop.low_stock() == ["banana", "hammer"]
    assert shop.low_stock(threshold=3) == ["hammer"]
    assert shop.low_stock(threshold=100) == ["apple", "banana", "hammer", "yo-yo"]


def test_value_by_category(ex, shop):
    assert shop.value_by_category() == {
        ex.Category.FOOD: 5.75,
        ex.Category.TOOLS: 24.0,
        ex.Category.TOYS: 24.5,
    }


def test_value_by_category_empty(ex):
    assert ex.Inventory().value_by_category() == {}


def test_by_location(shop):
    assert [item.name for item in shop.by_location()] == ["apple", "banana", "yo-yo", "hammer"]
