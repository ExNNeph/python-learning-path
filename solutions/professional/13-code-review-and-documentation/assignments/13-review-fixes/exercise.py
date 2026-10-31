"""Small invoice helpers. All money amounts are integer cents.

Template solution for assignment 13: every review comment is addressed, and every public
function documents itself with an example that doctest runs.
"""

import datetime
import re
import warnings
from collections import Counter

AMOUNT_RE = re.compile(r"([0-9]+)(?:[.,]([0-9]{1,2}))?")      # [0-9], not \d: \d also matches "١٢"


def add_line(lines, description, price_cents, qty=1):
    """Return a new list of invoice lines with one line added.

    The given list is not changed.

    >>> lines = add_line([], "Mort", 1250)
    >>> add_line(lines, "Dune", 990, qty=2)
    [{'description': 'Mort', 'price_cents': 1250, 'qty': 1}, {'description': 'Dune', 'price_cents': 990, 'qty': 2}]
    >>> lines
    [{'description': 'Mort', 'price_cents': 1250, 'qty': 1}]
    """
    return [*lines, {"description": description, "price_cents": price_cents, "qty": qty}]


def total(lines, tax_percent=19):
    """Return the total in cents including tax, rounded half up to a whole cent.

    >>> total([{"description": "Mort", "price_cents": 1000, "qty": 2}])
    2380
    >>> total([{"description": "Pen", "price_cents": 50, "qty": 1}], tax_percent=7)
    54
    """
    subtotal = sum(line["price_cents"] * line["qty"] for line in lines)
    # Integer arithmetic only: (x * 107 + 50) // 100 rounds x * 1.07 half up, with no float error.
    return (subtotal * (100 + tax_percent) + 50) // 100


def find_duplicates(lines):
    """Return the descriptions that occur more than once, in order of first appearance.

    >>> find_duplicates([{"description": d} for d in ["Pen", "Mort", "Pen", "Dune", "Mort", "Pen"]])
    ['Pen', 'Mort']
    """
    counts = Counter(line["description"] for line in lines)        # one pass instead of n²
    return [description for description, count in counts.items() if count > 1]


def parse_amount(text):
    """Parse a money amount like "12.50" or "12,50" into cents.

    At most two decimals; surrounding whitespace is ignored.

    Raises:
        ValueError: If the text is not a non-negative amount.

    >>> parse_amount("12,50")
    1250
    >>> parse_amount(" 7.5 ")
    750
    >>> parse_amount("twelve")
    Traceback (most recent call last):
    ValueError: not an amount: 'twelve'
    """
    match = AMOUNT_RE.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"not an amount: {text!r}")
    euros, cents = match.groups()
    return int(euros) * 100 + int((cents or "0").ljust(2, "0"))


def due_date(issued, days=30):
    """Return the due date `days` after `issued`, moved to Monday if it falls on a weekend.

    >>> due_date(datetime.date(2026, 11, 1), days=13)     # due on a Saturday
    datetime.date(2026, 11, 16)
    >>> due_date(datetime.date(2026, 11, 2))
    datetime.date(2026, 12, 2)
    """
    if days < 0:
        raise ValueError("days must not be negative")
    due = issued + datetime.timedelta(days=days)
    if due.weekday() >= 5:                                        # 5 = Saturday, 6 = Sunday
        due += datetime.timedelta(days=7 - due.weekday())
    return due


def calc(lines):
    """Deprecated: use total() instead.

    >>> import warnings
    >>> with warnings.catch_warnings():
    ...     warnings.simplefilter("ignore", DeprecationWarning)
    ...     calc([{"description": "Mort", "price_cents": 1000, "qty": 1}])
    1190
    """
    warnings.warn("calc() is deprecated, use total()", DeprecationWarning, stacklevel=2)
    return total(lines)


if __name__ == "__main__":
    import doctest

    print(doctest.testmod())
