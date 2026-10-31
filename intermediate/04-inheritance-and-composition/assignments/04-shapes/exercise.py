"""Assignment 04 · Shapes.

Replace each `raise NotImplementedError` with your code, and fill in the class bodies.
Check your work:  pytest intermediate/04-inheritance-and-composition/assignments/04-shapes -v
"""

import math
from abc import ABC, abstractmethod


class ShapeError(ValueError):
    """Raised for invalid shape dimensions."""


class Shape(ABC):
    """Abstract base class for all shapes."""

    # TODO: make area() and perimeter() abstract methods.

    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def describe(self):
        """Return e.g. 'Circle: area 3.14, perimeter 6.28'."""
        raise NotImplementedError


class Rectangle(Shape):
    def __init__(self, width, height):
        raise NotImplementedError

    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class Square(Rectangle):
    def __init__(self, side):
        raise NotImplementedError

    @property
    def side(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class Circle(Shape):
    def __init__(self, radius):
        raise NotImplementedError

    def area(self):
        raise NotImplementedError

    def perimeter(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class Drawing:
    """A collection of shapes (composition: it HAS shapes)."""

    def __init__(self):
        raise NotImplementedError

    def add(self, shape):
        """Add a shape and return self. Raise TypeError for anything that is not a Shape."""
        raise NotImplementedError

    def total_area(self):
        raise NotImplementedError

    def largest(self):
        """Return the shape with the largest area, or None if the drawing is empty."""
        raise NotImplementedError

    def count_by_type(self):
        """Return a dict mapping class names to counts."""
        raise NotImplementedError


if __name__ == "__main__":
    drawing = Drawing().add(Square(2)).add(Circle(1)).add(Rectangle(2, 5))
    for shape in (Square(2), Circle(1), Rectangle(2, 5)):
        print(shape.describe())
    print("Total area:", round(drawing.total_area(), 2))
    print("Largest:", drawing.largest())
