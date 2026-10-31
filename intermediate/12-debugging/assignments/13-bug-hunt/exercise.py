"""Assignment 13 · Bug hunt.

The docstrings are correct; the code has twelve bugs. Find and fix them.
Check your work:  pytest intermediate/12-debugging/assignments/13-bug-hunt -v
"""

import logging
from collections import Counter


def average_of_positives(numbers):
    """Return the average of the numbers > 0, or 0.0 if there are none."""
    total = 0
    for number in numbers:
        if number > 0:
            total += number
    return total / len(numbers)


def remove_short_words(words, min_length=3):
    """Return a NEW list without the words shorter than min_length."""
    for word in words:
        if len(word) < min_length:
            words.remove(word)
    return words


def add_tag(tag, tags=[]):
    """Return a list with tag appended; without tags, start from a new empty list."""
    tags.append(tag)
    return tags


def make_grid(rows, cols, fill=0):
    """Return a rows x cols grid (list of lists) with independent rows."""
    return [[fill] * cols] * rows


def find_index(items, target):
    """Return the index of the first target in items, or -1."""
    i = 0
    while i < len(items) - 1:
        if items[i] == target:
            return i
        i += 1
    return -1


def parse_config(text):
    """Parse 'key = value' lines (split at the first '='), skipping blanks and '#' comments."""
    config = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=")
        config[key.strip()] = value.strip()
    return config


def apply_discount(price, percent):
    """Return price reduced by percent %, rounded to 2 decimals."""
    return round(price * (100 - percent) // 100, 2)


def shipping_cost(weight):
    """4.99 below 1 kg, 6.99 below 5 kg, else 6.99 + 0.50 per kg over 5 (rounded)."""
    if weight <= 0:
        raise ValueError("weight must be positive")
    if weight < 1:
        return 4.99
    elif weight < 5:
        return 6.99
    else:
        cost = round(6.99 + (weight - 5) * 0.50, 2)


def make_multipliers(n):
    """Return n functions; the one at index i multiplies its argument by i."""
    return [lambda x: x * i for i in range(n)]


def count_words(text):
    """Count words case-insensitively, ignoring .,!?;: around them."""
    words = (word.strip(".,!?;:") for word in text.split())
    return Counter(word for word in words if word)


def process_orders(orders):
    """Return the sum of valid amounts; log a warning for each invalid order.

    An order is a dict with "id" and "amount". Invalid: a missing amount
    (reason "missing amount") or an amount <= 0 (reason "amount must be positive").
    Warning text: "skipping order <id>: <reason>".
    """
    total = 0
    for order in orders:
        amount = order.get("amount")
        if amount is None:
            print(f"skipping order {order['id']}: missing amount")
        elif amount <= 0:
            print(f"skipping order {order['id']}: amount must be positive")
        else:
            total += amount
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(average_of_positives([3, -1, 5]))
    print(make_grid(2, 3))
    print(process_orders([{"id": 1, "amount": 20}, {"id": 2}, {"id": 3, "amount": -5}]))
