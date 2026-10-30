"""Assignment 14 · Safe calculator.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/10-errors-and-exceptions/assignments/14-safe-calculator -v
"""


def parse_number(text):
    """Return text as a float (spaces and decimal comma allowed).

    Raise ValueError("not a number: '<text>'") if it is not a number.
    """
    raise NotImplementedError


def calculate(a, operator, b):
    """Return a <operator> b for +, -, *, /.

    Raise ZeroDivisionError("cannot divide by zero") for division by 0 and
    ValueError("unknown operator: '<operator>'") for any other operator.
    """
    raise NotImplementedError


def evaluate(expression):
    """Return the result of '<number> <operator> <number>' (parts separated by spaces).

    Raise ValueError("expected: <number> <operator> <number>") if there are not exactly 3 parts.
    """
    raise NotImplementedError


def safe_evaluate(expression):
    """Return the result as text (f"{result:g}") or 'Error: <message>'. Never raise."""
    raise NotImplementedError


def main():
    print("Type an expression like 3 + 4, or quit.")
    while True:
        expression = input("> ").strip()
        if expression.lower() == "quit":
            break
        print(safe_evaluate(expression))


if __name__ == "__main__":
    main()
