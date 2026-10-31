# Assignment 05 · Validated fields

> **Lesson:** [04 · Attribute access](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Build a small validation library with **descriptors**, the technique behind model fields in Django,
SQLAlchemy and pydantic. Then write a cached property (a non-data descriptor) and a read-only config
object with `__getattr__` and `__setattr__`.

```python
class Product:
    name = Typed(str)
    price = Typed(int, float)
    quantity = Range(min=0)
    size = OneOf("S", "M", "L")

    def __init__(self, name, price, quantity, size):
        self.name, self.price, self.quantity, self.size = name, price, quantity, size
```

## What to write

| Name | Specification |
|---|---|
| `Field` | the base descriptor. `__set_name__` remembers the attribute name. `__get__` returns the descriptor itself when accessed on the class, else the value stored in the **instance's `__dict__`**; a value that was never set raises `AttributeError` (with the attribute name in the message). `__set__` calls `self.validate(value)` and then stores the value. `validate` does nothing in `Field` |
| `Typed(*types)` | a `Field` whose `validate` raises `TypeError("<name> must be int or float, got str")` unless `isinstance(value, types)` (types joined with `" or "`) |
| `Range(min=None, max=None)` | a `Field` for numbers: `ValueError("<name> must be >= <min>, got <value>")` or `"... <= <max> ..."`. `None` means no bound |
| `OneOf(*options)` | a `Field`: `ValueError("<name> must be one of 'S', 'M', 'L', got 'XL'")` (options with `repr`, joined by `", "`) |
| `lazy_property` | a decorator like `functools.cached_property`: the first access calls the method and stores the result in the instance's `__dict__` **under the same name**; later accesses never call the method again. Only `__get__`, no `__set__` |
| `Config(mapping)` | read-only, attribute-style access to a nested dict: `config.database.host`. Nested dicts come back as `Config` objects. A missing key: `AttributeError`. **Any** assignment `config.x = ...` raises `AttributeError`. `config["key"]` is not needed |

Each field must keep its value per **instance**: two products must not share a price.

## Examples

```python
>>> shirt = Product("Shirt", 19.99, 3, "M")
>>> shirt.price = "cheap"
Traceback (most recent call last):
TypeError: price must be int or float, got str
>>> shirt.quantity = -1
Traceback (most recent call last):
ValueError: quantity must be >= 0, got -1
>>> shirt.size = "XL"
Traceback (most recent call last):
ValueError: size must be one of 'S', 'M', 'L', got 'XL'
>>> vars(shirt)
{'name': 'Shirt', 'price': 19.99, 'quantity': 3, 'size': 'M'}

>>> class Report:
...     @lazy_property
...     def total(self):
...         print("computing...")
...         return 42
>>> r = Report()
>>> r.total
computing...
42
>>> r.total
42

>>> config = Config({"debug": True, "database": {"host": "localhost", "port": 5432}})
>>> config.database.port
5432
>>> config.debug = False
Traceback (most recent call last):
AttributeError: Config is read-only
```

## Hints

<details>
<summary>Hint 1: Field</summary>

`__set_name__(self, owner, name)` stores `self.name = name`. In `__get__`, after the `instance is None`
check, use `instance.__dict__[self.name]` inside a `try` and turn the `KeyError` into an
`AttributeError`. The subclasses only override `validate` (and `__init__` to store their options;
remember to call `super().__init__()` if `Field` has one).
</details>

<details>
<summary>Hint 2: lazy_property</summary>

`lazy_property(func)` is a class: `__init__` stores the function, `__set_name__` stores the name,
`__get__` computes `value = self.func(instance)`, saves it with `instance.__dict__[self.name] = value`
and returns it. Because there is no `__set__`, the instance dict wins from now on.
</details>

<details>
<summary>Hint 3: Config</summary>

Store the dict with `object.__setattr__(self, "_data", mapping)`, because your own `__setattr__`
refuses everything. `__getattr__` only runs for missing attributes, so `self._data` inside it is safe.
Wrap dict values in `Config` before returning them.
</details>

## Check your work

```bash
pytest advanced/04-attribute-access/assignments/05-validated-fields -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/04-attribute-access/assignments/05-validated-fields/exercise.py),
then tick off assignment 05 in the [progress checklist](../../../../README.md#progress-checklist).
