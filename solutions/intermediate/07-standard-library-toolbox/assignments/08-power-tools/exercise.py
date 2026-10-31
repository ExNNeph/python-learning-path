"""Assignment 08 · Power tools: template solution."""

from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
from functools import lru_cache
from itertools import combinations, groupby
from operator import itemgetter


def top_words(text, n):
    """Return the n most common lower-cased words as (word, count) pairs."""
    # Ties keep the order in which the words first appeared.
    return Counter(text.lower().split()).most_common(n)


def group_by_length(words):
    """Return a plain dict: length -> list of words in original order."""
    groups = defaultdict(list)
    for word in words:
        groups[len(word)].append(word)      # no "is the key there yet?" check needed
    # A plain dict for the caller: reading a missing key should raise, not create it.
    return dict(groups)


def totals_by_customer(orders):
    """Return a dict customer -> total amount, customers in alphabetical order."""
    by_customer = itemgetter("customer")
    # groupby only merges NEIGHBOURS, so sort by the same key first.
    ordered = sorted(orders, key=by_customer)
    return {customer: sum(order["amount"] for order in group)
            for customer, group in groupby(ordered, key=by_customer)}


def last_n(iterable, n):
    """Return the last n items as a list, storing at most n items."""
    # The deque drops its oldest item whenever a new one arrives: memory stays at n.
    return list(deque(iterable, maxlen=n))


def pairs(items):
    """Return all unordered pairs as a list of tuples."""
    return list(combinations(items, 2))


@lru_cache(maxsize=None)
def count_paths(steps):
    """Return the number of ways to climb `steps` stairs with steps of 1, 2 or 3."""
    if steps < 0:
        return 0            # overshot: not a valid way
    if steps == 0:
        return 1            # exactly at the top: one way (take no more steps)
    # Without the cache this makes ~1.8^steps calls; with it, each value is computed once.
    return count_paths(steps - 1) + count_paths(steps - 2) + count_paths(steps - 3)


def weekdays_between(start, end):
    """Return the number of Mon-Fri days from start to end (ISO strings), both included."""
    day, last = date.fromisoformat(start), date.fromisoformat(end)
    count = 0
    while day <= last:                      # end before start: the loop never runs → 0
        if day.weekday() < 5:               # Monday = 0 ... Friday = 4
            count += 1
        day += timedelta(days=1)
    return count


def duration_minutes(start, end):
    """Return the minutes between two 'HH:MM' times. end before start: ValueError."""
    begin = datetime.strptime(start, "%H:%M")
    finish = datetime.strptime(end, "%H:%M")
    if finish < begin:
        raise ValueError(f"end {end} is before start {start}")
    return int((finish - begin).total_seconds() // 60)


if __name__ == "__main__":
    print(top_words("to be or not to be that is the question", 2))
    print("Ways to climb 50 stairs:", count_paths(50))
    print("Workdays in November 2026:", weekdays_between("2026-11-01", "2026-11-30"))
