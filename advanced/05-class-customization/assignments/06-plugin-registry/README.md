# Assignment 06 · Plugin registry

> **Lesson:** [05 · Class customization](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Write the class-level machinery of a small plugin framework: plugins that register themselves just by
being defined, a class decorator that writes `__repr__` for you, a singleton metaclass, and a function
that builds record classes at run time.

## What to write

### `Plugin`: a self-registering base class

| Member | Specification |
|---|---|
| `Plugin.registry` | a dict `{name: plugin class}`, shared by all plugins |
| `class X(Plugin)` | registers `X` under its class name in lower case |
| `class X(Plugin, name="csv")` | registers it under the given name |
| `class X(Plugin, abstract=True)` | is **not** registered and not checked: an intermediate base class for other plugins |
| checks | a registered plugin must define a callable `run` (its own or inherited, but not just `Plugin`'s). Otherwise: `TypeError` at class creation. A name that is already taken: `TypeError` as well |
| `Plugin.create(name, *args, **kwargs)` | class method: creates an instance of the plugin registered under `name`. Unknown name: `LookupError("no plugin named '<name>'")` |

### `@auto_repr`

A class decorator that adds a `__repr__` built from the parameter names of the class's `__init__`:
`Point(x=1, y=2)`. It reads each value from the attribute of the same name. Returns the same class.

### `Singleton`

A metaclass: `class Settings(metaclass=Singleton)`: every call `Settings(...)` returns the **same**
instance (`__init__` runs only the first time). Each class using it has its own single instance.

### `record(name, *fields)`

Builds a new class at run time with `type()`. Its instances take the fields as positional or keyword
arguments, have a `__repr__` like `Point(x=1, y=2)`, and compare equal (`==`) when they are of the same
record class and all fields are equal. Missing or extra arguments: `TypeError`.

## Examples

```python
>>> class Csv(Plugin, name="csv"):
...     def run(self, rows):
...         return "\n".join(",".join(map(str, row)) for row in rows)
>>> Plugin.create("csv").run([(1, 2), (3, 4)])
'1,2\n3,4'
>>> class Broken(Plugin):
...     pass
Traceback (most recent call last):
TypeError: plugin Broken must define run()

>>> @auto_repr
... class Point:
...     def __init__(self, x, y):
...         self.x, self.y = x, y
>>> Point(1, 2)
Point(x=1, y=2)

>>> class Settings(metaclass=Singleton):
...     def __init__(self, debug=False):
...         self.debug = debug
>>> Settings(debug=True) is Settings()
True

>>> Color = record("Color", "red", "green", "blue")
>>> Color(255, 128, blue=0)
Color(red=255, green=128, blue=0)
>>> Color(1, 2, 3) == Color(1, 2, 3)
True
```

## Hints

<details>
<summary>Hint 1: Plugin.__init_subclass__</summary>

`def __init_subclass__(cls, *, name=None, abstract=False, **kwargs)`: call `super().__init_subclass__(**kwargs)`
first, return early for `abstract`. To check `run`: `getattr(cls, "run", None)` finds it in the whole MRO;
compare it against `Plugin.run` (if you give `Plugin` a `run` at all) or just check `callable(...)`.
Register in `Plugin.registry`, not `cls.registry` (which would be the same dict here, but says what you mean).
</details>

<details>
<summary>Hint 2: auto_repr</summary>

`inspect.signature(cls.__init__).parameters` lists `self` too: skip the first one. Build the text with
`getattr(self, name)` for each parameter. Assign the function with `cls.__repr__ = __repr__`.
</details>

<details>
<summary>Hint 3: Singleton and record</summary>

`Singleton.__call__(cls, *args, **kwargs)` runs whenever the class is called: keep a dict keyed by the
class and call `super().__call__(*args, **kwargs)` only on the first call.

For `record`, write `__init__(self, *args, **kwargs)`, `__repr__` and `__eq__` as inner functions that
use `fields` from the closure. A neat way to check the arguments: `inspect.Signature` with one
`inspect.Parameter(field, inspect.Parameter.POSITIONAL_OR_KEYWORD)` per field, then `.bind(*args, **kwargs)`
raises `TypeError` for you. Finally: `return type(name, (), {"__init__": ..., ...})`.
</details>

## Check your work

```bash
pytest advanced/05-class-customization/assignments/06-plugin-registry -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/05-class-customization/assignments/06-plugin-registry/exercise.py),
then tick off assignment 06 in the [progress checklist](../../../../README.md#progress-checklist).
