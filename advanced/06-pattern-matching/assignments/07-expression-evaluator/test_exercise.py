"""Tests for assignment 07. Run: pytest advanced/06-pattern-matching/assignments/07-expression-evaluator -v"""

import pytest


@pytest.fixture
def n(ex):
    """Short constructors: n.num(2), n.var("x"), n.op("+", a, b), n.neg(a)."""
    class Nodes:
        num, var, neg, op = ex.Num, ex.Var, ex.Neg, ex.BinOp
    return Nodes


# --- evaluate ----------------------------------------------------------------

def test_evaluate_leaves(ex, n):
    assert ex.evaluate(n.num(7)) == 7
    assert ex.evaluate(n.var("x"), {"x": 3}) == 3


def test_evaluate_tree(ex, n):
    expr = n.op("+", n.num(2), n.op("*", n.var("x"), n.num(3)))
    assert ex.evaluate(expr, {"x": 4}) == 14


@pytest.mark.parametrize("op, expected", [("+", 8), ("-", 4), ("*", 12), ("/", 3.0)])
def test_evaluate_operators(ex, n, op, expected):
    assert ex.evaluate(n.op(op, n.num(6), n.num(2))) == expected


def test_evaluate_neg(ex, n):
    assert ex.evaluate(n.neg(n.op("-", n.num(1), n.num(5)))) == 4


def test_evaluate_undefined_variable(ex, n):
    with pytest.raises(NameError, match="undefined variable: 'y'"):
        ex.evaluate(n.op("+", n.var("x"), n.var("y")), {"x": 1})


def test_evaluate_unknown_operator(ex, n):
    with pytest.raises(ValueError, match="unknown operator: '%'"):
        ex.evaluate(n.op("%", n.num(1), n.num(2)))


def test_evaluate_not_a_node(ex, n):
    with pytest.raises(TypeError, match="not an expression"):
        ex.evaluate(n.op("+", n.num(1), 2))


def test_evaluate_division_by_zero(ex, n):
    with pytest.raises(ZeroDivisionError):
        ex.evaluate(n.op("/", n.num(1), n.num(0)))


# --- simplify ----------------------------------------------------------------

def test_simplify_folds_constants(ex, n):
    assert ex.simplify(n.op("*", n.op("+", n.num(1), n.num(2)), n.num(4))) == n.num(12)


@pytest.mark.parametrize("make", [
    lambda n, x: n.op("+", x, n.num(0)),
    lambda n, x: n.op("+", n.num(0), x),
    lambda n, x: n.op("-", x, n.num(0)),
    lambda n, x: n.op("*", x, n.num(1)),
    lambda n, x: n.op("*", n.num(1), x),
    lambda n, x: n.op("/", x, n.num(1)),
    lambda n, x: n.neg(n.neg(x)),
])
def test_simplify_identities(ex, n, make):
    x = n.op("+", n.var("a"), n.var("b"))
    assert ex.simplify(make(n, x)) == x


def test_simplify_times_zero(ex, n):
    assert ex.simplify(n.op("*", n.var("x"), n.num(0))) == n.num(0)
    assert ex.simplify(n.op("*", n.num(0), n.op("+", n.var("x"), n.var("y")))) == n.num(0)


def test_simplify_x_minus_x(ex, n):
    x = n.op("*", n.var("a"), n.num(2))
    assert ex.simplify(n.op("-", x, x)) == n.num(0)
    assert ex.simplify(n.op("-", n.var("a"), n.var("b"))) == n.op("-", n.var("a"), n.var("b"))


def test_simplify_neg_num(ex, n):
    assert ex.simplify(n.neg(n.num(3))) == n.num(-3)


def test_simplify_is_bottom_up(ex, n):
    expr = n.op("*", n.op("+", n.var("y"), n.num(0)), n.op("-", n.num(5), n.num(4)))
    assert ex.simplify(expr) == n.var("y")


def test_simplify_deep(ex, n):
    expr = n.neg(n.neg(n.op("+", n.op("*", n.num(0), n.var("z")), n.op("-", n.var("q"), n.num(0)))))
    assert ex.simplify(expr) == n.var("q")


def test_simplify_keeps_division_by_zero(ex, n):
    expr = n.op("/", n.num(1), n.num(0))
    assert ex.simplify(expr) == expr


def test_simplify_leaves_irreducible_alone(ex, n):
    expr = n.op("+", n.var("x"), n.op("*", n.num(2), n.var("y")))
    assert ex.simplify(expr) == expr
    assert ex.simplify(n.var("x")) == n.var("x")


# --- to_text -----------------------------------------------------------------

def test_to_text(ex, n):
    expr = n.op("+", n.num(2), n.op("*", n.var("x"), n.num(3)))
    assert ex.to_text(expr) == "(2 + (x * 3))"
    assert ex.to_text(n.neg(n.var("x"))) == "-x"
    assert ex.to_text(n.neg(n.op("-", n.num(1.5), n.var("y")))) == "-(1.5 - y)"


# --- parse_command -----------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("", ("noop",)),
    ("   ", ("noop",)),
    ("look", ("look",)),
    ("L", ("look",)),
    ("go north", ("go", "north")),
    ("Go  WEST", ("go", "west")),
    ("north", ("go", "north")),
    ("s", ("go", "south")),
    ("go e", ("go", "east")),
    ("take lamp", ("take", "lamp")),
    ("  Take  BRASS lamp ", ("take", "brass lamp")),
    ("take", ("error", "take what?")),
    ("drop all", ("drop_all",)),
    ("drop lamp", ("drop", "lamp")),
    ("drop", ("error", "drop what?")),
    ("quit", ("quit",)),
    ("EXIT", ("quit",)),
    ("q", ("quit",)),
])
def test_parse_command(ex, text, expected):
    assert ex.parse_command(text) == expected


@pytest.mark.parametrize("text", ["dance wildly", "go", "go up", "north east", "look around"])
def test_parse_command_unknown(ex, text):
    assert ex.parse_command(f" {text} ") == ("error", f"I don't understand {text!r}")


# --- route_event -------------------------------------------------------------

@pytest.mark.parametrize("event, expected", [
    ({"type": "click", "pos": [3, 4]}, "left click at (3, 4)"),
    ({"type": "click", "pos": [3, 4], "button": "right", "ts": 17}, "right click at (3, 4)"),
    ({"type": "key", "key": "s"}, "key s"),
    ({"type": "key", "key": "s", "mods": ["ctrl", "shift"]}, "key ctrl+shift+s"),
    ({"type": "key", "key": "x", "mods": []}, "key x"),
    ({"type": "resize", "size": {"width": 800, "height": 600}}, "resize to 800x600"),
    ({"type": "scroll", "delta": 3}, "unknown event 'scroll'"),
])
def test_route_event(ex, event, expected):
    assert ex.route_event(event) == expected


@pytest.mark.parametrize("event, kind", [
    ({"type": "click", "pos": [3]}, "click"),
    ({"type": "click", "pos": ["3", 4]}, "click"),
    ({"type": "click", "pos": [3, 4], "button": 2}, "click"),
    ({"type": "key"}, "key"),
    ({"type": "key", "key": "s", "mods": ["ctrl", 1]}, "key"),
    ({"type": "key", "key": "s", "mods": "ctrl"}, "key"),
    ({"type": "resize", "size": {"width": 0, "height": 600}}, "resize"),
    ({"type": "resize", "size": [800, 600]}, "resize"),
    ({"type": "batch", "events": "nope"}, "batch"),
])
def test_route_event_invalid_shape(ex, event, kind):
    assert ex.route_event(event) == f"invalid {kind} event"


@pytest.mark.parametrize("event", [None, 42, "click", [1, 2], {}, {"pos": [1, 2]}, {"type": 5}])
def test_route_event_invalid(ex, event):
    assert ex.route_event(event) == "invalid event"


def test_route_event_batch(ex):
    event = {"type": "batch", "events": [
        {"type": "click", "pos": [1, 2]},
        {"type": "scroll"},
        {"type": "batch", "events": [{"type": "key", "key": "q"}]},
    ]}
    assert ex.route_event(event) == "left click at (1, 2); unknown event 'scroll'; key q"
    assert ex.route_event({"type": "batch", "events": []}) == ""
