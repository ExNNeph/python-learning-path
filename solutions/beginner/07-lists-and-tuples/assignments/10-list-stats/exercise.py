"""Assignment 10 · List statistics: template solution."""


def mean(numbers):
    """Return the average of numbers, or None for an empty list."""
    # Guard first: without it, an empty list would raise ZeroDivisionError.
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def median(numbers):
    """Return the middle value (average of the two middle values for an even count), or None."""
    if not numbers:
        return None
    # sorted() returns a NEW list. numbers.sort() would reorder the caller's list,
    # a side effect nobody expects from a function that only "computes" something.
    ordered = sorted(numbers)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    # Even count: e.g. 4 items → indexes 1 and 2 are the middle pair.
    return (ordered[middle - 1] + ordered[middle]) / 2


def min_max(numbers):
    """Return (smallest, largest) using a loop (no min()/max()), or None for an empty list."""
    if not numbers:
        return None
    # Start from a real item, not from 0: with [-5, -2], a start of 0 would wrongly
    # report 0 as the largest number.
    smallest = largest = numbers[0]
    for n in numbers[1:]:
        if n < smallest:
            smallest = n
        elif n > largest:          # a number cannot be both, so elif is safe
            largest = n
    return smallest, largest       # packing: two values become one tuple


def running_total(numbers):
    """Return a new list of cumulative sums: [1, 2, 3] -> [1, 3, 6]."""
    # Two accumulators: one number (the sum so far) and one list (the results).
    totals = []
    total = 0
    for n in numbers:
        total += n
        totals.append(total)
    return totals


def remove_duplicates(items):
    """Return a new list without repeats, keeping the order of first appearance."""
    result = []
    for item in items:
        # `in` on a list checks every item, so this is fine for small lists but slow
        # for huge ones. Lesson 08 adds a set for O(1) "seen before?" checks.
        if item not in result:
            result.append(item)
    return result


def top_n(numbers, n):
    """Return a new list with the n largest numbers, largest first."""
    # Slicing never raises IndexError, so n larger than the list just returns everything.
    return sorted(numbers, reverse=True)[:n]


if __name__ == "__main__":
    data = [70, 95, 82, 61, 95, 88]
    print("mean:", mean(data), "median:", median(data), "range:", min_max(data))
    print("top 3:", top_n(data, 3))
