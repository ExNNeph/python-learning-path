"""Assignment 13 · Bug hunt: template solution.

Each fix is marked with BUG: the name of the bug and why the old code failed.
"""

import logging
from collections import Counter

logger = logging.getLogger(__name__)


def average_of_positives(numbers):
    """Return the average of the numbers > 0, or 0.0 if there are none."""
    # BUG 1 (wrong count): the old code divided by len(numbers), counting negatives too.
    # BUG 2 (missing empty case): with no positives it divided by zero or returned 0 / n.
    positives = [number for number in numbers if number > 0]
    if not positives:
        return 0.0
    return sum(positives) / len(positives)


def remove_short_words(words, min_length=3):
    """Return a NEW list without the words shorter than min_length."""
    # BUG 3 (changing a list while looping over it): remove() shifted the remaining items,
    # so the loop skipped the word after each removed one, AND it changed the caller's list.
    return [word for word in words if len(word) >= min_length]


def add_tag(tag, tags=None):
    """Return a list with tag appended; without tags, start from a new empty list."""
    # BUG 4 (mutable default argument): `tags=[]` was created once, so every call without
    # tags appended to the same list. None + a new list inside fixes it.
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


def make_grid(rows, cols, fill=0):
    """Return a rows x cols grid (list of lists) with independent rows."""
    # BUG 5 (aliasing): `[row] * rows` repeated a reference to ONE row list.
    return [[fill] * cols for _ in range(rows)]


def find_index(items, target):
    """Return the index of the first target in items, or -1."""
    # BUG 6 (off-by-one): `len(items) - 1` never looked at the last item.
    # enumerate() avoids manual index bookkeeping altogether.
    for index, item in enumerate(items):
        if item == target:
            return index
    return -1


def parse_config(text):
    """Parse 'key = value' lines (split at the first '='), skipping blanks and '#' comments."""
    config = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # BUG 7 (splitting at every '='): a value like "a=b" gave three parts and a ValueError.
        # partition() splits at the FIRST '=' only.
        key, _, value = line.partition("=")
        config[key.strip()] = value.strip()
    return config


def apply_discount(price, percent):
    """Return price reduced by percent %, rounded to 2 decimals."""
    # BUG 8 (integer division): // rounded DOWN to a whole number before round() ran.
    return round(price * (100 - percent) / 100, 2)


def shipping_cost(weight):
    """4.99 below 1 kg, 6.99 below 5 kg, else 6.99 + 0.50 per kg over 5 (rounded)."""
    if weight <= 0:
        raise ValueError("weight must be positive")
    if weight < 1:
        return 4.99
    if weight < 5:
        return 6.99
    # BUG 9 (missing return): the last branch computed the cost and then fell off the end
    # of the function, which returns None.
    return round(6.99 + (weight - 5) * 0.50, 2)


def make_multipliers(n):
    """Return n functions; the one at index i multiplies its argument by i."""
    # BUG 10 (late binding): every lambda looked up `i` when CALLED, after the loop had
    # finished, so all of them used the last i. The default argument i=i captures the value
    # at creation time (a factory function, lesson 02, works too).
    return [lambda x, i=i: x * i for i in range(n)]


def count_words(text):
    """Count words case-insensitively, ignoring .,!?;: around them."""
    # BUG 11 (case sensitivity): "The" and "the" were counted as different words.
    words = (word.strip(".,!?;:") for word in text.lower().split())
    return Counter(word for word in words if word)


def process_orders(orders):
    """Return the sum of valid amounts; log a warning for each invalid order."""
    total = 0
    for order in orders:
        amount = order.get("amount")
        # BUG 12 (print instead of logging): warnings belong in the log, where they get a
        # level and a timestamp and can be routed or silenced, not on stdout mixed with output.
        if amount is None:
            logger.warning("skipping order %s: %s", order["id"], "missing amount")
        elif amount <= 0:
            logger.warning("skipping order %s: %s", order["id"], "amount must be positive")
        else:
            total += amount
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(average_of_positives([3, -1, 5]))
    print(make_grid(2, 3))
    print(process_orders([{"id": 1, "amount": 20}, {"id": 2}, {"id": 3, "amount": -5}]))
