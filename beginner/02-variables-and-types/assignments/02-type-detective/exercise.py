"""Assignment 02 · Type detective.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/02-variables-and-types/assignments/02-type-detective -v
"""


def type_name(value):
    """Return the name of the value's type, e.g. 'int' for 42 and 'NoneType' for None."""
    raise NotImplementedError


def describe(value):
    """Return '<value> is of type <type name>', e.g. '3.5 is of type float'."""
    raise NotImplementedError


def add_numeric_strings(a, b):
    """Return the sum of two digit strings as an int: ('3', '4') -> 7."""
    raise NotImplementedError


def swap(a, b):
    """Return the two values in swapped order: (1, 'a') -> ('a', 1)."""
    raise NotImplementedError


def same_object(a, b):
    """Return True if a and b are the very same object (not just equal values)."""
    raise NotImplementedError


if __name__ == "__main__":
    for value in [42, 4.2, "42", True, None]:
        print(describe(value))
