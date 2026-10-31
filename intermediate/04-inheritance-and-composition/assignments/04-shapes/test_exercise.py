"""Tests for assignment 04. Run: pytest intermediate/04-inheritance-and-composition/assignments/04-shapes -v"""

import math

import pytest


def test_shape_error_is_a_value_error(ex):
    assert issubclass(ex.ShapeError, ValueError)


def test_shape_is_abstract(ex):
    with pytest.raises(TypeError):
        ex.Shape()


def test_subclass_without_area_cannot_be_created(ex):
    class Blob(ex.Shape):
        def perimeter(self):
            return 1

    with pytest.raises(TypeError):
        Blob()


def test_inheritance_tree(ex):
    assert issubclass(ex.Rectangle, ex.Shape)
    assert issubclass(ex.Circle, ex.Shape)
    assert issubclass(ex.Square, ex.Rectangle)
    assert not issubclass(ex.Drawing, list)


def test_rectangle(ex):
    rect = ex.Rectangle(2, 3)
    assert rect.area() == 6
    assert rect.perimeter() == 10
    assert repr(rect) == "Rectangle(width=2, height=3)"


def test_square(ex):
    square = ex.Square(2)
    assert square.side == 2
    assert square.area() == 4
    assert square.perimeter() == 8
    assert repr(square) == "Square(side=2)"


def test_square_uses_rectangle_init(ex, monkeypatch):
    calls = []
    original = ex.Rectangle.__init__

    def spy(self, width, height):
        calls.append((width, height))
        original(self, width, height)

    monkeypatch.setattr(ex.Rectangle, "__init__", spy)
    ex.Square(3)
    assert calls == [(3, 3)]


def test_circle(ex):
    circle = ex.Circle(1)
    assert circle.area() == pytest.approx(math.pi)
    assert circle.perimeter() == pytest.approx(2 * math.pi)
    assert repr(circle) == "Circle(radius=1)"


@pytest.mark.parametrize("make", [
    lambda ex: ex.Rectangle(0, 5),
    lambda ex: ex.Rectangle(5, -1),
    lambda ex: ex.Square(0),
])
def test_invalid_rectangles(ex, make):
    with pytest.raises(ex.ShapeError, match="width and height must be positive"):
        make(ex)


@pytest.mark.parametrize("radius", [0, -2])
def test_invalid_circle(ex, radius):
    with pytest.raises(ex.ShapeError, match="radius must be positive"):
        ex.Circle(radius)


def test_describe(ex):
    assert ex.Circle(1).describe() == "Circle: area 3.14, perimeter 6.28"
    assert ex.Square(2).describe() == "Square: area 4.00, perimeter 8.00"
    assert ex.Rectangle(2, 5).describe() == "Rectangle: area 10.00, perimeter 14.00"


def test_describe_is_inherited(ex):
    assert "describe" not in vars(ex.Circle)
    assert "describe" not in vars(ex.Rectangle)


def test_drawing_add_is_chainable(ex):
    drawing = ex.Drawing()
    assert drawing.add(ex.Circle(1)) is drawing


@pytest.mark.parametrize("thing", ["circle", 3, None, [1, 2]])
def test_drawing_rejects_non_shapes(ex, thing):
    with pytest.raises(TypeError):
        ex.Drawing().add(thing)


def test_drawing_total_area(ex):
    drawing = ex.Drawing().add(ex.Square(2)).add(ex.Circle(1)).add(ex.Circle(2))
    assert drawing.total_area() == pytest.approx(4 + 5 * math.pi)
    assert ex.Drawing().total_area() == 0


def test_drawing_largest(ex):
    big = ex.Circle(2)
    drawing = ex.Drawing().add(ex.Square(2)).add(big).add(ex.Circle(1))
    assert drawing.largest() is big
    assert ex.Drawing().largest() is None


def test_drawing_count_by_type(ex):
    drawing = ex.Drawing().add(ex.Square(2)).add(ex.Circle(1)).add(ex.Circle(2))
    assert drawing.count_by_type() == {"Square": 1, "Circle": 2}
    assert ex.Drawing().count_by_type() == {}


def test_drawing_accepts_any_shape_subclass(ex):
    class Triangle(ex.Shape):
        def area(self):
            return 1.5

        def perimeter(self):
            return 6

    drawing = ex.Drawing().add(Triangle())
    assert drawing.total_area() == 1.5
    assert drawing.count_by_type() == {"Triangle": 1}


def test_drawings_are_independent(ex):
    first, second = ex.Drawing(), ex.Drawing()
    first.add(ex.Circle(1))
    assert second.total_area() == 0
