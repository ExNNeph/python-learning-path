"""Assignment 05 · Receipt printer.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/04-input-and-output/assignments/05-receipt-printer -v
"""


def parse_price(text):
    """Return the price in `text` as a float: ' 3,50 ' -> 3.5."""
    raise NotImplementedError


def format_line(label, amount, width=24):
    """Return one receipt line of exactly `width` characters:

    >>> format_line("Coffee x3", 10.5)
    'Coffee x3..........10.50'
    """
    raise NotImplementedError


def main():
    """Ask for 'Item: ', 'Price: ' and 'Quantity: ', then print the receipt:

    Coffee x3..........10.50
    ------------------------
    TOTAL..............10.50
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
