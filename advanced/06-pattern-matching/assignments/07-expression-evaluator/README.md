# Assignment 07 · Expression evaluator

> **Lesson:** [06 · Structural pattern matching](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2.5 h

## Goal

Use `match` on three kinds of structured data: **expression trees** (class patterns and recursion),
**text commands** (sequence patterns) and **JSON events** (mapping patterns). Not a single `isinstance`
or `len()` check is needed; the patterns do all of it.

## Part 1 · Expression trees

The node classes are given (frozen dataclasses, so they have `__match_args__`):

```python
Num(value)                 # a number: Num(2)
Var(name)                  # a variable: Var("x")
Neg(operand)               # minus: Neg(Var("x")) is -x
BinOp(op, left, right)     # op is "+", "-", "*" or "/": BinOp("+", Num(2), Var("x")) is 2 + x
```

| Function | Specification |
|---|---|
| `evaluate(node, env=None)` | the value of the expression. `env` maps variable names to numbers. Unknown variable: `NameError("undefined variable: 'x'")`. Unknown operator: `ValueError("unknown operator: '%'")`. Something that is not a node: `TypeError("not an expression: <repr>")`. Division by zero raises `ZeroDivisionError` as usual |
| `simplify(node)` | a simplified tree, built **bottom-up** (simplify the children first). Rules below. Variables stay variables |
| `to_text(node)` | infix text: numbers and names as they are, every `BinOp` in brackets `(a + b)`, `Neg` as `-x` |

Simplification rules (`x` is any expression):

| Pattern | Result |
|---|---|
| a `BinOp` of two `Num`s | the computed `Num` (except division by zero: leave it as it is) |
| `x + 0`, `0 + x`, `x - 0` | `x` |
| `x * 1`, `1 * x`, `x / 1` | `x` |
| `x * 0`, `0 * x` | `Num(0)` |
| `x - x` (equal subtrees) | `Num(0)` |
| `Neg(Num(v))` | `Num(-v)` |
| `Neg(Neg(x))` | `x` |

## Part 2 · Text commands

`parse_command(text)` for a text adventure. Case-insensitive; extra spaces do not matter.

| Input | Result |
|---|---|
| empty | `("noop",)` |
| `look`, `l` | `("look",)` |
| `go north`, `north`, `n` (also south/east/west, s/e/w) | `("go", "north")`, always the long direction name |
| `take brass lamp` | `("take", "brass lamp")`; `take` alone: `("error", "take what?")` |
| `drop all` / `drop lamp` | `("drop_all",)` / `("drop", "lamp")`; `drop` alone: `("error", "drop what?")` |
| `quit`, `exit`, `q` | `("quit",)` |
| anything else | `("error", "I don't understand 'dance wildly'")` with the input as typed, but stripped |

## Part 3 · JSON events

`route_event(event)` receives decoded JSON (any value) and returns a description:

| Event | Result |
|---|---|
| `{"type": "click", "pos": [x, y]}` with int `x`, `y`, and an optional str `"button"` (default `"left"`) | `"left click at (3, 4)"` |
| `{"type": "key", "key": k}` with a str `k`, and an optional `"mods"` list of strs | `"key s"`, `"key ctrl+shift+s"` |
| `{"type": "resize", "size": {"width": w, "height": h}}` with **positive** ints | `"resize to 800x600"` |
| `{"type": "batch", "events": [...]}` | the results of all inner events joined with `"; "` |
| one of these four types, but the wrong shape | `"invalid click event"` (with the type) |
| any other str type | `"unknown event 'scroll'"` |
| anything else (no dict, no `"type"`, a non-str type) | `"invalid event"` |

Extra keys in an event are always ignored.

## Examples

```python
>>> expr = BinOp("+", Num(2), BinOp("*", Var("x"), Num(3)))
>>> evaluate(expr, {"x": 4})
14
>>> to_text(expr)
'(2 + (x * 3))'
>>> simplify(BinOp("*", BinOp("+", Var("y"), Num(0)), BinOp("-", Num(5), Num(4))))
Var(name='y')
>>> parse_command("  Take  BRASS lamp ")
('take', 'brass lamp')
>>> parse_command("n")
('go', 'north')
>>> route_event({"type": "key", "key": "s", "mods": ["ctrl", "shift"]})
'key ctrl+shift+s'
>>> route_event({"type": "batch", "events": [{"type": "click", "pos": [1, 2]}, {"type": "scroll"}]})
"left click at (1, 2); unknown event 'scroll'"
```

## Hints

<details>
<summary>Hint 1: evaluate and to_text</summary>

One case per node class: `case Num(value): ...`, `case BinOp(op, left, right): ...`. Inside the
`BinOp` case, evaluate both sides and pick the operation with a small dict of `operator` functions
(or a nested `match op:`). Finish with `case _:` for the `TypeError`.
</details>

<details>
<summary>Hint 2: simplify</summary>

First rebuild the node from simplified children, then `match` the **new** node against the rules. For
"two equal subtrees" use a guard: `case BinOp("-", left, right) if left == right:` (dataclasses compare
by value). Order the cases so that constant folding comes first.
</details>

<details>
<summary>Hint 3: commands and events</summary>

Match on `text.lower().split()`. A capture with OR and `as` normalises directions:
`case ["go", ("north" | "n") ] | ["north" | "n"]:` works but repeats itself; a small dict
`{"n": "north", ...}` plus a guard `if word in DIRECTIONS` is shorter.

For events, a pattern like `{"type": "click", "pos": [int(x), int(y)]}` checks the shape and the types.
Write the case **with** `"button": str(button)` first, then the one without. `"mods": [*mods]` captures
a list; check "all strings" in a guard.
</details>

## Check your work

```bash
pytest advanced/06-pattern-matching/assignments/07-expression-evaluator -v
```

## Done?

Compare with the [template solution](../../../../solutions/advanced/06-pattern-matching/assignments/07-expression-evaluator/exercise.py),
then tick off assignment 07 in the [progress checklist](../../../../README.md#progress-checklist).
