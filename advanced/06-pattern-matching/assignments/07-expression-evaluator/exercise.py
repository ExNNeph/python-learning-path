"""Assignment 07 · Expression evaluator.

Replace each `raise NotImplementedError` with your code. Use `match` for all three parts.
Check your work:  pytest advanced/06-pattern-matching/assignments/07-expression-evaluator -v
"""

import operator
from dataclasses import dataclass


# --- the expression tree (given) -----------------------------------------------

@dataclass(frozen=True)
class Num:
    value: float


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Neg:
    operand: object


@dataclass(frozen=True)
class BinOp:
    op: str
    left: object
    right: object


# --- Part 1 · expression trees -------------------------------------------------

def evaluate(node, env=None):
    """Compute the value of the expression tree; env maps variable names to numbers."""
    raise NotImplementedError


def simplify(node):
    """Return a simplified tree (see the rules in the README)."""
    raise NotImplementedError


def to_text(node):
    """Infix text: every BinOp in brackets, Neg as -x."""
    raise NotImplementedError


# --- Part 2 · text commands ----------------------------------------------------

def parse_command(text):
    """Parse an adventure command into a tuple like ("go", "north")."""
    raise NotImplementedError


# --- Part 3 · JSON events ------------------------------------------------------

def route_event(event):
    """Describe a decoded JSON event, e.g. 'left click at (3, 4)'."""
    raise NotImplementedError


if __name__ == "__main__":
    expr = BinOp("+", Num(2), BinOp("*", Var("x"), Num(3)))
    print(to_text(expr), "=", evaluate(expr, {"x": 4}))
    print(parse_command("take brass lamp"))
    print(route_event({"type": "click", "pos": [3, 4], "button": "right"}))
