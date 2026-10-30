"""Assignment 02 · Type detective: template solution."""


def type_name(value):
    """Return the name of the value's type, e.g. 'int' for 42 and 'NoneType' for None."""
    # type(value) returns the type object itself (<class 'int'>).
    # Every type knows its own name in the attribute __name__.
    return type(value).__name__


def describe(value):
    """Return '<value> is of type <type name>', e.g. '3.5 is of type float'."""
    # str() is needed because Python never mixes text and numbers silently
    # (strong typing): "x" + 3.5 would raise a TypeError.
    # Reusing type_name keeps the "how do I get the name" logic in one place.
    return str(value) + " is of type " + type_name(value)


def add_numeric_strings(a, b):
    """Return the sum of two digit strings as an int: ('3', '4') -> 7."""
    # a + b on strings would join them: "3" + "4" == "34".
    # Converting first makes + mean addition.
    return int(a) + int(b)


def swap(a, b):
    """Return the two values in swapped order: (1, 'a') -> ('a', 1)."""
    # No temporary variable needed: the caller can write x, y = swap(x, y).
    # Inside a function you could also write a, b = b, a; the right side is
    # evaluated completely before any name is rebound.
    return b, a


def same_object(a, b):
    """Return True if a and b are the very same object (not just equal values)."""
    # `is` compares identity (like id(a) == id(b)); `==` would compare values,
    # and [1, 2] == [1, 2] is True even for two different lists.
    return a is b


if __name__ == "__main__":
    for value in [42, 4.2, "42", True, None]:
        print(describe(value))
