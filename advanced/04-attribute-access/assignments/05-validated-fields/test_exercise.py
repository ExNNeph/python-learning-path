"""Tests for assignment 05. Run: pytest advanced/04-attribute-access/assignments/05-validated-fields -v"""

import pytest


@pytest.fixture
def Product(ex):
    class Product:
        name = ex.Typed(str)
        price = ex.Typed(int, float)
        quantity = ex.Range(min=0)
        rating = ex.Range(min=1, max=5)
        size = ex.OneOf("S", "M", "L")
        note = ex.Field()

        def __init__(self, name, price, quantity, size, rating=3):
            self.name, self.price, self.quantity, self.size, self.rating = name, price, quantity, size, rating

    return Product


# --- Field -------------------------------------------------------------------

def test_values_live_in_the_instance_dict(Product):
    shirt = Product("Shirt", 19.99, 3, "M")
    assert vars(shirt) == {"name": "Shirt", "price": 19.99, "quantity": 3, "size": "M", "rating": 3}
    assert (shirt.name, shirt.price, shirt.quantity, shirt.size) == ("Shirt", 19.99, 3, "M")


def test_values_are_per_instance(Product):
    a = Product("A", 1, 1, "S")
    b = Product("B", 2, 2, "L")
    a.price = 100
    assert (a.price, b.price) == (100, 2)


def test_class_access_returns_descriptor(ex, Product):
    assert isinstance(Product.price, ex.Typed)
    assert isinstance(Product.note, ex.Field)


def test_set_name_learns_the_name(Product):
    assert Product.price.name == "price"
    assert Product.size.name == "size"


def test_field_accepts_everything(Product):
    shirt = Product("Shirt", 1, 1, "S")
    shirt.note = ["anything", 1]
    assert shirt.note == ["anything", 1]


def test_unset_field_is_attribute_error(Product):
    shirt = Product("Shirt", 1, 1, "S")
    with pytest.raises(AttributeError, match="note"):
        shirt.note
    assert not hasattr(shirt, "note")
    assert getattr(shirt, "note", "default") == "default"


def test_data_descriptor_wins_over_instance_dict(Product):
    shirt = Product("Shirt", 1, 1, "S")
    with pytest.raises(ValueError):
        shirt.quantity = -5
    assert shirt.quantity == 1


def test_subclasses_inherit_from_field(ex):
    assert issubclass(ex.Typed, ex.Field)
    assert issubclass(ex.Range, ex.Field)
    assert issubclass(ex.OneOf, ex.Field)


# --- Typed / Range / OneOf ---------------------------------------------------

def test_typed(Product):
    shirt = Product("Shirt", 19.99, 3, "M")
    shirt.price = 20
    with pytest.raises(TypeError, match="^price must be int or float, got str$"):
        shirt.price = "cheap"
    with pytest.raises(TypeError, match="^name must be str, got int$"):
        shirt.name = 5
    assert shirt.price == 20


def test_validation_runs_in_init(Product):
    with pytest.raises(TypeError):
        Product(None, 1, 1, "S")
    with pytest.raises(ValueError):
        Product("X", 1, -1, "S")


def test_range(Product):
    shirt = Product("Shirt", 1, 0, "S")
    shirt.quantity = 10**9
    with pytest.raises(ValueError, match="^quantity must be >= 0, got -1$"):
        shirt.quantity = -1
    shirt.rating = 5
    with pytest.raises(ValueError, match="^rating must be <= 5, got 6$"):
        shirt.rating = 6
    with pytest.raises(ValueError, match="^rating must be >= 1, got 0$"):
        shirt.rating = 0


def test_range_without_bounds(ex):
    class Anything:
        value = ex.Range()

    a = Anything()
    a.value = -10**12
    assert a.value == -10**12


def test_one_of(Product):
    shirt = Product("Shirt", 1, 1, "S")
    shirt.size = "L"
    with pytest.raises(ValueError, match=r"^size must be one of 'S', 'M', 'L', got 'XL'$"):
        shirt.size = "XL"
    assert shirt.size == "L"


# --- lazy_property -----------------------------------------------------------

def test_lazy_property_computes_once(ex):
    calls = []

    class Report:
        @ex.lazy_property
        def total(self):
            calls.append(1)
            return 42

    r = Report()
    assert (r.total, r.total, r.total) == (42, 42, 42)
    assert len(calls) == 1
    assert vars(r) == {"total": 42}


def test_lazy_property_per_instance(ex):
    class Square:
        def __init__(self, n):
            self.n = n

        @ex.lazy_property
        def area(self):
            return self.n * self.n

    assert (Square(3).area, Square(4).area) == (9, 16)


def test_lazy_property_is_non_data(ex):
    class Report:
        @ex.lazy_property
        def total(self):
            return 1

    assert not hasattr(ex.lazy_property, "__set__")
    r = Report()
    r.total = 99                    # allowed: goes into the instance dict
    assert r.total == 99
    assert isinstance(Report.total, ex.lazy_property)


def test_lazy_property_recomputes_after_delete(ex):
    calls = []

    class Report:
        @ex.lazy_property
        def total(self):
            calls.append(1)
            return len(calls)

    r = Report()
    assert r.total == 1
    del r.total
    assert r.total == 2


# --- Config ------------------------------------------------------------------

@pytest.fixture
def config(ex):
    return ex.Config({"debug": True, "name": "shop", "database": {"host": "localhost", "port": 5432, "options": {"ssl": False}}})


def test_config_attributes(config):
    assert config.debug is True
    assert config.name == "shop"


def test_config_nested(ex, config):
    assert isinstance(config.database, ex.Config)
    assert config.database.host == "localhost"
    assert config.database.options.ssl is False


def test_config_missing_is_attribute_error(config):
    with pytest.raises(AttributeError):
        config.timeout
    assert getattr(config, "timeout", 30) == 30
    assert not hasattr(config.database, "user")


def test_config_is_read_only(config):
    with pytest.raises(AttributeError, match="read-only"):
        config.debug = False
    with pytest.raises(AttributeError, match="read-only"):
        config.new_key = 1
    assert config.debug is True


def test_config_keys_like_methods_are_values(ex):
    config = ex.Config({"items": [1, 2], "keys": "k"})
    assert config.items == [1, 2]
    assert config.keys == "k"
