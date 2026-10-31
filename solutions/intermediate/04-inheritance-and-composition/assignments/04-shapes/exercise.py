"""Assignment 04 · Shapes: template solution."""

import math
from abc import ABC, abstractmethod


class ShapeError(ValueError):
    """Raised for invalid shape dimensions."""
    # Subclassing ValueError: callers can catch our specific ShapeError, and generic code
    # that already catches ValueError keeps working.


class Shape(ABC):
    """Abstract base class for all shapes."""

    @abstractmethod
    def area(self):
        """Return the area."""

    @abstractmethod
    def perimeter(self):
        """Return the perimeter."""

    def describe(self):
        """Return e.g. 'Circle: area 3.14, perimeter 6.28'."""
        # Written once, works for every subclass: type(self) is the real class, and
        # self.area() runs the subclass's implementation.
        return f"{type(self).__name__}: area {self.area():.2f}, perimeter {self.perimeter():.2f}"


class Rectangle(Shape):
    def __init__(self, width, height):
        if width <= 0 or height <= 0:
            raise ShapeError("width and height must be positive")
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def __repr__(self):
        return f"Rectangle(width={self.width!r}, height={self.height!r})"


class Square(Rectangle):
    # A square IS a rectangle with equal sides, and it can be used wherever a rectangle
    # is expected, so inheritance fits. Everything except __init__ and __repr__ is inherited,
    # including the validation.
    def __init__(self, side):
        super().__init__(side, side)

    @property
    def side(self):
        return self.width

    def __repr__(self):
        return f"Square(side={self.side!r})"


class Circle(Shape):
    def __init__(self, radius):
        if radius <= 0:
            raise ShapeError("radius must be positive")
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

    def __repr__(self):
        return f"Circle(radius={self.radius!r})"


class Drawing:
    """A collection of shapes (composition: it HAS shapes)."""

    def __init__(self):
        # Composition: the list is an implementation detail. Subclassing list would also
        # expose insert, sort, extend ... which would bypass the type check in add().
        self._shapes = []

    def add(self, shape):
        """Add a shape and return self. Raise TypeError for anything that is not a Shape."""
        # The one place where we check the type: this is a trust boundary, and a wrong
        # object here would only fail much later inside total_area().
        if not isinstance(shape, Shape):
            raise TypeError(f"expected a Shape, got {type(shape).__name__}")
        self._shapes.append(shape)
        return self                       # returning self makes add() chainable

    def total_area(self):
        # Polymorphism: no isinstance checks, every shape knows its own area.
        return sum(shape.area() for shape in self._shapes)

    def largest(self):
        """Return the shape with the largest area, or None if the drawing is empty."""
        return max(self._shapes, key=lambda shape: shape.area(), default=None)

    def count_by_type(self):
        """Return a dict mapping class names to counts."""
        counts = {}
        for shape in self._shapes:
            name = type(shape).__name__
            counts[name] = counts.get(name, 0) + 1
        return counts


if __name__ == "__main__":
    drawing = Drawing().add(Square(2)).add(Circle(1)).add(Rectangle(2, 5))
    for shape in (Square(2), Circle(1), Rectangle(2, 5)):
        print(shape.describe())
    print("Total area:", round(drawing.total_area(), 2))
    print("Largest:", drawing.largest())
