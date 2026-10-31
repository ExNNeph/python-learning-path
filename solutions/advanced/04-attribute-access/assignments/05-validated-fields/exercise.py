"""Assignment 05 · Validated fields: template solution."""


class Field:
    """Base descriptor: stores the value in the instance's __dict__ after validate(value).

    One Field object lives on the class and serves every instance, so the value itself must be
    stored on the instance. Using the same name as the attribute keeps vars(obj) readable.
    """

    name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self                  # Product.price: the descriptor itself, for introspection
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{type(instance).__name__!r} object has no attribute {self.name!r}") from None

    def __set__(self, instance, value):  # having __set__ makes this a DATA descriptor: it wins over __dict__
        self.validate(value)
        instance.__dict__[self.name] = value

    def validate(self, value):
        """Raise an exception for invalid values. The base class accepts everything."""


class Typed(Field):
    def __init__(self, *types):
        self.types = types

    def validate(self, value):
        if not isinstance(value, self.types):
            expected = " or ".join(t.__name__ for t in self.types)
            raise TypeError(f"{self.name} must be {expected}, got {type(value).__name__}")


class Range(Field):
    def __init__(self, min=None, max=None):
        self.min, self.max = min, max

    def validate(self, value):
        if self.min is not None and value < self.min:
            raise ValueError(f"{self.name} must be >= {self.min}, got {value}")
        if self.max is not None and value > self.max:
            raise ValueError(f"{self.name} must be <= {self.max}, got {value}")


class OneOf(Field):
    def __init__(self, *options):
        self.options = options

    def validate(self, value):
        if value not in self.options:
            allowed = ", ".join(map(repr, self.options))
            raise ValueError(f"{self.name} must be one of {allowed}, got {value!r}")


class lazy_property:
    """A NON-data descriptor (no __set__): once the value sits in the instance dict, the normal
    lookup finds it first and __get__ is never called again."""

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.name] = value
        return value


class Config:
    """Read-only attribute access to a nested dict: config.database.host."""

    def __init__(self, mapping):
        object.__setattr__(self, "_data", dict(mapping))   # our own __setattr__ refuses everything

    def __getattr__(self, name):                           # only called for names not found normally
        try:
            value = self._data[name]
        except KeyError:
            raise AttributeError(f"no config key {name!r}") from None
        return Config(value) if isinstance(value, dict) else value

    def __setattr__(self, name, value):
        raise AttributeError("Config is read-only")

    def __delattr__(self, name):
        raise AttributeError("Config is read-only")

    def __repr__(self):
        return f"Config({self._data!r})"


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
