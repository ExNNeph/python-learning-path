"""Assignment 05 · Validated fields.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/04-attribute-access/assignments/05-validated-fields -v
"""


class Field:
    """Base descriptor: stores the value in the instance's __dict__ after validate(value)."""

    def __set_name__(self, owner, name):
        raise NotImplementedError

    def __get__(self, instance, owner):
        raise NotImplementedError

    def __set__(self, instance, value):
        raise NotImplementedError

    def validate(self, value):
        """Raise an exception for invalid values. The base class accepts everything."""


class Typed(Field):
    """Typed(int, float): TypeError unless isinstance(value, types)."""

    def __init__(self, *types):
        raise NotImplementedError


class Range(Field):
    """Range(min=0, max=100): ValueError outside the bounds (None = no bound)."""

    def __init__(self, min=None, max=None):
        raise NotImplementedError


class OneOf(Field):
    """OneOf("S", "M", "L"): ValueError for any other value."""

    def __init__(self, *options):
        raise NotImplementedError


class lazy_property:
    """Like functools.cached_property: compute on first access, then store in the instance dict."""

    def __init__(self, func):
        raise NotImplementedError


class Config:
    """Read-only attribute access to a nested dict: config.database.host."""

    def __init__(self, mapping):
        raise NotImplementedError


if __name__ == "__main__":
    class Product:
        name = Typed(str)
        price = Typed(int, float)
        quantity = Range(min=0)
        size = OneOf("S", "M", "L")

        def __init__(self, name, price, quantity, size):
            self.name, self.price, self.quantity, self.size = name, price, quantity, size

    shirt = Product("Shirt", 19.99, 3, "M")
    print(vars(shirt))
    try:
        shirt.size = "XL"
    except ValueError as error:
        print("rejected:", error)
