"""Assignment 06 · Plugin registry: template solution."""

import inspect


class Plugin:
    """Base class: every subclass registers itself in Plugin.registry (see the README)."""

    registry = {}

    def __init_subclass__(cls, *, name=None, abstract=False, **kwargs):
        super().__init_subclass__(**kwargs)          # cooperate with other base classes
        if abstract:
            return                                   # intermediate base class: no checks, no entry
        if not callable(getattr(cls, "run", None)):
            # Fail when the class is DEFINED, not when someone first tries to run the plugin.
            raise TypeError(f"plugin {cls.__name__} must define run()")
        key = name or cls.__name__.lower()
        if key in Plugin.registry:
            raise TypeError(f"plugin name {key!r} is already taken by {Plugin.registry[key].__name__}")
        Plugin.registry[key] = cls

    @classmethod
    def create(cls, name, *args, **kwargs):
        try:
            plugin_class = Plugin.registry[name]
        except KeyError:
            raise LookupError(f"no plugin named {name!r}") from None
        return plugin_class(*args, **kwargs)


def auto_repr(cls):
    # Skip `self`: the first parameter of __init__.
    names = list(inspect.signature(cls.__init__).parameters)[1:]

    def __repr__(self):
        args = ", ".join(f"{n}={getattr(self, n)!r}" for n in names)
        return f"{type(self).__name__}({args})"

    cls.__repr__ = __repr__
    return cls                                       # decorate, don't replace


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Settings() is a call on the class object, so it lands here, in the metaclass.
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return Singleton._instances[cls]


def record(name, *fields):
    signature = inspect.Signature(
        [inspect.Parameter(field, inspect.Parameter.POSITIONAL_OR_KEYWORD) for field in fields]
    )

    def __init__(self, *args, **kwargs):
        bound = signature.bind(*args, **kwargs)      # TypeError for missing / extra / duplicate args
        for field, value in bound.arguments.items():
            setattr(self, field, value)

    def __repr__(self):
        values = ", ".join(f"{f}={getattr(self, f)!r}" for f in fields)
        return f"{name}({values})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return all(getattr(self, f) == getattr(other, f) for f in fields)

    namespace = {"__init__": __init__, "__repr__": __repr__, "__eq__": __eq__, "_fields": fields}
    return type(name, (), namespace)                 # what the class statement does for us normally


if __name__ == "__main__":
    class Shout(Plugin):
        def run(self, text):
            return text.upper() + "!"

    print(Plugin.registry)
    print(Plugin.create("shout").run("plugins work"))
