"""Assignment 06 · Plugin registry.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest advanced/05-class-customization/assignments/06-plugin-registry -v
"""

import inspect


class Plugin:
    """Base class: every subclass registers itself in Plugin.registry (see the README)."""

    registry = {}

    def __init_subclass__(cls, *, name=None, abstract=False, **kwargs):
        raise NotImplementedError

    @classmethod
    def create(cls, name, *args, **kwargs):
        """Instantiate the plugin registered under name; unknown: LookupError."""
        raise NotImplementedError


def auto_repr(cls):
    """Class decorator: add __repr__ built from the __init__ parameters, e.g. Point(x=1, y=2)."""
    raise NotImplementedError


class Singleton(type):
    """Metaclass: every class using it has exactly one instance."""


def record(name, *fields):
    """Build a class `name` with the given fields, __init__, __repr__ and __eq__, using type()."""
    raise NotImplementedError


if __name__ == "__main__":
    class Shout(Plugin):
        def run(self, text):
            return text.upper() + "!"

    print(Plugin.registry)
    print(Plugin.create("shout").run("plugins work"))
