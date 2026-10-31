"""Assignment 07 · Expression evaluator: template solution."""

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


OPERATORS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}


# --- Part 1 · expression trees -------------------------------------------------

def evaluate(node, env=None):
    env = env or {}
    match node:
        case Num(value):
            return value
        case Var(name):
            if name not in env:
                raise NameError(f"undefined variable: {name!r}")
            return env[name]
        case Neg(operand):
            return -evaluate(operand, env)
        case BinOp(op, left, right):
            if op not in OPERATORS:
                raise ValueError(f"unknown operator: {op!r}")
            return OPERATORS[op](evaluate(left, env), evaluate(right, env))
        case _:
            raise TypeError(f"not an expression: {node!r}")


def simplify(node):
    # Bottom-up: simplify the children first, then look at the rebuilt node.
    match node:
        case Neg(operand):
            node = Neg(simplify(operand))
        case BinOp(op, left, right):
            node = BinOp(op, simplify(left), simplify(right))

    match node:
        case BinOp("/", Num(), Num(0)):
            return node                                   # keep 1 / 0 for evaluate() to report
        case BinOp(op, Num(a), Num(b)) if op in OPERATORS:
            return Num(OPERATORS[op](a, b))
        case BinOp("+", x, Num(0)) | BinOp("+", Num(0), x) | BinOp("-", x, Num(0)):
            return x
        case BinOp("*", x, Num(1)) | BinOp("*", Num(1), x) | BinOp("/", x, Num(1)):
            return x
        case BinOp("*", _, Num(0)) | BinOp("*", Num(0), _):
            return Num(0)
        case BinOp("-", left, right) if left == right:    # dataclasses compare by value
            return Num(0)
        case Neg(Num(value)):
            return Num(-value)
        case Neg(Neg(x)):
            return x
        case _:
            return node


def to_text(node):
    match node:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Neg(operand):
            return f"-{to_text(operand)}"
        case BinOp(op, left, right):
            return f"({to_text(left)} {op} {to_text(right)})"
        case _:
            raise TypeError(f"not an expression: {node!r}")


# --- Part 2 · text commands ----------------------------------------------------

DIRECTIONS = {"n": "north", "s": "south", "e": "east", "w": "west",
              "north": "north", "south": "south", "east": "east", "west": "west"}


def parse_command(text):
    match text.lower().split():
        case []:
            return ("noop",)
        case ["look" | "l"]:
            return ("look",)
        case ["go", word] | [word] if word in DIRECTIONS:
            return ("go", DIRECTIONS[word])
        case ["take"]:
            return ("error", "take what?")
        case ["take", *item]:
            return ("take", " ".join(item))
        case ["drop"]:
            return ("error", "drop what?")
        case ["drop", "all"]:
            return ("drop_all",)
        case ["drop", *item]:
            return ("drop", " ".join(item))
        case ["quit" | "exit" | "q"]:
            return ("quit",)
        case _:
            return ("error", f"I don't understand {text.strip()!r}")


# --- Part 3 · JSON events ------------------------------------------------------

def route_event(event):
    match event:
        case {"type": "click", "pos": [int(x), int(y)], "button": str(button)}:
            return f"{button} click at ({x}, {y})"
        case {"type": "click", "pos": [int(x), int(y)]} if "button" not in event:
            return f"left click at ({x}, {y})"
        case {"type": "key", "key": str(key), "mods": [*mods]} if all(isinstance(m, str) for m in mods):
            return "key " + "+".join([*mods, key])
        case {"type": "key", "key": str(key)} if "mods" not in event:
            return f"key {key}"
        case {"type": "resize", "size": {"width": int(w), "height": int(h)}} if w > 0 and h > 0:
            return f"resize to {w}x{h}"
        case {"type": "batch", "events": [*events]}:
            return "; ".join(route_event(inner) for inner in events)
        case {"type": "click" | "key" | "resize" | "batch" as kind}:
            return f"invalid {kind} event"
        case {"type": str(kind)}:
            return f"unknown event {kind!r}"
        case _:
            return "invalid event"


if __name__ == "__main__":
    expr = BinOp("+", Num(2), BinOp("*", Var("x"), Num(3)))
    print(to_text(expr), "=", evaluate(expr, {"x": 4}))
    print(parse_command("take brass lamp"))
    print(route_event({"type": "click", "pos": [3, 4], "button": "right"}))
