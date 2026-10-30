"""Assignment 14 · Safe calculator: template solution."""


def parse_number(text):
    """Return text as a float (spaces and decimal comma allowed)."""
    # EAFP: just try the conversion. Checking first (isdigit) would reject valid input
    # such as "-3" or "2.5".
    try:
        return float(text.strip().replace(",", "."))
    except ValueError:
        # Replace Python's generic message with one that names the bad input.
        # "from None" hides the original exception, which adds nothing here.
        raise ValueError(f"not a number: '{text}'") from None


def calculate(a, operator, b):
    """Return a <operator> b for +, -, *, /."""
    if operator == "+":
        return a + b
    if operator == "-":
        return a - b
    if operator == "*":
        return a * b
    if operator == "/":
        # Python would raise ZeroDivisionError by itself ("float division by zero"),
        # but checking first lets us give the user a clearer message.
        if b == 0:
            raise ZeroDivisionError("cannot divide by zero")
        return a / b
    # Every known operator returned above; anything that gets here is invalid.
    raise ValueError(f"unknown operator: '{operator}'")


def evaluate(expression):
    """Return the result of '<number> <operator> <number>' (parts separated by spaces)."""
    parts = expression.split()
    if len(parts) != 3:
        raise ValueError("expected: <number> <operator> <number>")
    left, operator, right = parts
    # No try/except here on purpose: this function cannot fix bad input,
    # so it lets the exceptions travel up to a caller that can.
    return calculate(parse_number(left), operator, parse_number(right))


def safe_evaluate(expression):
    """Return the result as text (f"{result:g}") or 'Error: <message>'. Never raise."""
    # The one place that catches: the boundary between the program and the user.
    # Only the two exceptions we expect are caught; a real bug (say a TypeError
    # from a typo in this file) would still crash loudly, as it should.
    try:
        result = evaluate(expression)
    except (ValueError, ZeroDivisionError) as error:
        return f"Error: {error}"
    # else-style: formatting stays outside the try block, so it cannot be swallowed.
    return f"{result:g}"


def main():
    print("Type an expression like 3 + 4, or quit.")
    while True:
        expression = input("> ").strip()
        if expression.lower() == "quit":
            break
        print(safe_evaluate(expression))


if __name__ == "__main__":
    main()
