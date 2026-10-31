"""Tests for assignment 06. Run: pytest advanced/05-class-customization/assignments/06-plugin-registry -v"""

import pytest


# --- Plugin ------------------------------------------------------------------

def test_subclass_registers_itself(ex):
    class Shout(ex.Plugin):
        def run(self, text):
            return text.upper()

    assert ex.Plugin.registry == {"shout": Shout}


def test_custom_name(ex):
    class CsvExport(ex.Plugin, name="csv"):
        def run(self, rows):
            return "\n".join(",".join(map(str, row)) for row in rows)

    assert ex.Plugin.registry == {"csv": CsvExport}
    assert ex.Plugin.create("csv").run([(1, 2), (3, 4)]) == "1,2\n3,4"


def test_create_passes_arguments(ex):
    class Greeter(ex.Plugin):
        def __init__(self, greeting, *, punctuation="!"):
            self.greeting, self.punctuation = greeting, punctuation

        def run(self, name):
            return f"{self.greeting}, {name}{self.punctuation}"

    assert ex.Plugin.create("greeter", "Hi", punctuation="?").run("Ada") == "Hi, Ada?"


def test_create_unknown(ex):
    with pytest.raises(LookupError, match="no plugin named 'nope'"):
        ex.Plugin.create("nope")


def test_missing_run_fails_at_definition(ex):
    with pytest.raises(TypeError, match="Broken"):
        class Broken(ex.Plugin):
            pass
    assert ex.Plugin.registry == {}


def test_non_callable_run_fails(ex):
    with pytest.raises(TypeError):
        class Broken(ex.Plugin):
            run = 42


def test_abstract_base_is_not_registered(ex):
    class TextPlugin(ex.Plugin, abstract=True):
        def clean(self, text):
            return text.strip()

    class Strip(TextPlugin):
        def run(self, text):
            return self.clean(text)

    assert ex.Plugin.registry == {"strip": Strip}
    assert ex.Plugin.create("strip").run("  x ") == "x"


def test_inherited_run_counts(ex):
    class Base(ex.Plugin, abstract=True):
        def run(self):
            return type(self).__name__

    class Alpha(Base):
        pass

    class Beta(Base, name="b"):
        pass

    assert ex.Plugin.registry == {"alpha": Alpha, "b": Beta}
    assert ex.Plugin.create("b").run() == "Beta"


def test_duplicate_name(ex):
    class One(ex.Plugin, name="dup"):
        def run(self):
            pass

    with pytest.raises(TypeError, match="dup"):
        class Two(ex.Plugin, name="dup"):
            def run(self):
                pass

    assert ex.Plugin.registry == {"dup": One}


def test_subclass_of_plugin_is_registered_too(ex):
    class Base(ex.Plugin):
        def run(self):
            return 1

    class Child(Base):
        pass

    assert set(ex.Plugin.registry) == {"base", "child"}


def test_cooperates_with_other_init_subclass(ex):
    seen = []

    class Tracker:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            seen.append(cls.__name__)

    class Tracked(ex.Plugin, Tracker):
        def run(self):
            pass

    assert seen == ["Tracked"]
    assert "tracked" in ex.Plugin.registry


# --- auto_repr ---------------------------------------------------------------

def test_auto_repr(ex):
    @ex.auto_repr
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

    assert repr(Point(1, 2)) == "Point(x=1, y=2)"
    assert repr(Point("a", [3])) == "Point(x='a', y=[3])"


def test_auto_repr_returns_the_same_class(ex):
    class Thing:
        def __init__(self, name):
            self.name = name

    assert ex.auto_repr(Thing) is Thing
    assert repr(Thing("box")) == "Thing(name='box')"


def test_auto_repr_with_defaults_and_keyword_only(ex):
    @ex.auto_repr
    class Box:
        def __init__(self, width, height=1, *, label="box"):
            self.width, self.height, self.label = width, height, label

    assert repr(Box(3)) == "Box(width=3, height=1, label='box')"


def test_auto_repr_uses_subclass_name(ex):
    @ex.auto_repr
    class Animal:
        def __init__(self, name):
            self.name = name

    class Dog(Animal):
        pass

    assert repr(Dog("Rex")) == "Dog(name='Rex')"


# --- Singleton ---------------------------------------------------------------

def test_singleton(ex):
    created = []

    class Settings(metaclass=ex.Singleton):
        def __init__(self, debug=False):
            created.append(1)
            self.debug = debug

    first = Settings(debug=True)
    second = Settings()
    assert first is second
    assert second.debug is True
    assert len(created) == 1


def test_singleton_per_class(ex):
    class A(metaclass=ex.Singleton):
        pass

    class B(metaclass=ex.Singleton):
        pass

    assert A() is A()
    assert A() is not B()
    assert isinstance(B(), B)


def test_singleton_is_a_metaclass(ex):
    assert issubclass(ex.Singleton, type)


# --- record ------------------------------------------------------------------

def test_record_creates_a_class(ex):
    Color = ex.record("Color", "red", "green", "blue")
    assert isinstance(Color, type)
    assert Color.__name__ == "Color"


def test_record_init_and_repr(ex):
    Color = ex.record("Color", "red", "green", "blue")
    c = Color(255, 128, blue=0)
    assert (c.red, c.green, c.blue) == (255, 128, 0)
    assert repr(c) == "Color(red=255, green=128, blue=0)"


def test_record_equality(ex):
    Point = ex.record("Point", "x", "y")
    Other = ex.record("Other", "x", "y")
    assert Point(1, 2) == Point(x=1, y=2)
    assert Point(1, 2) != Point(2, 1)
    assert Point(1, 2) != Other(1, 2)
    assert Point(1, 2) != (1, 2)


@pytest.mark.parametrize("args, kwargs", [((1,), {}), ((1, 2, 3), {}), ((1, 2), {"z": 3}), ((1,), {"x": 2})])
def test_record_wrong_arguments(ex, args, kwargs):
    Point = ex.record("Point", "x", "y")
    with pytest.raises(TypeError):
        Point(*args, **kwargs)


def test_records_are_independent(ex):
    A = ex.record("A", "one")
    B = ex.record("B", "two", "three")
    assert repr(A(1)) == "A(one=1)"
    assert repr(B(2, 3)) == "B(two=2, three=3)"
