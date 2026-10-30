"""Assignment 05 · Receipt printer: template solution."""


def parse_price(text):
    """Return the price in `text` as a float: ' 3,50 ' -> 3.5."""
    # Clean first, convert last: float() accepts surrounding spaces, but not a comma.
    # Chaining works because every string method returns a new string.
    return float(text.strip().replace(",", "."))


def format_line(label, amount, width=24):
    """Return one receipt line of exactly `width` characters."""
    # Build the right-hand part first, because its length decides how many dots fit.
    amount_text = f"{amount:.2f}"
    dots = "." * (width - len(label) - len(amount_text))
    return label + dots + amount_text
    # Shorter but harder to read: f"{label:.<{width - len(amount_text)}}{amount_text}"


def main():
    """Ask for item, price and quantity, then print the receipt."""
    # All input() and print() calls live here; the functions above stay pure
    # (same input → same output, no side effects), so the tests can check them directly.
    item = input("Item: ")
    price = parse_price(input("Price: "))
    quantity = int(input("Quantity: "))

    total = price * quantity
    print(format_line(f"{item} x{quantity}", total))
    print("-" * 24)
    print(format_line("TOTAL", total))


if __name__ == "__main__":
    main()
