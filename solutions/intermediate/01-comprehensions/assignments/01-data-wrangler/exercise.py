"""Assignment 01 · Data wrangler: template solution."""


def positive_squares(numbers):
    """Return a list of the squares of the numbers greater than 0, in order."""
    # expression first, filter last: "n * n, for every n, if n > 0"
    return [n * n for n in numbers if n > 0]


def clean_names(raw):
    """Return the stripped, title-cased names; drop empty and blank entries."""
    # name.strip() is "" for blank entries, and "" is falsy, so the filter drops them.
    # We strip twice; for a tiny list that is clearer than a helper variable.
    return [name.strip().title() for name in raw if name.strip()]


def email_domains(emails):
    """Return the set of lower-cased domains (the part after '@')."""
    # rpartition splits at the LAST '@' and always returns three parts, so even an
    # odd address cannot raise an IndexError. A set comprehension removes duplicates.
    return {email.rpartition("@")[2].lower() for email in emails}


def word_lengths(words):
    """Return a dict mapping each word to its length."""
    return {word: len(word) for word in words}


def invert(mapping):
    """Return a dict with keys and values swapped.

    Raise ValueError("values are not unique") if two keys share a value.
    """
    inverted = {value: key for key, value in mapping.items()}
    # Duplicate values become duplicate keys, and a dict keeps only the last one,
    # so the inverted dict is shorter. Checking the length catches it without a loop.
    if len(inverted) != len(mapping):
        raise ValueError("values are not unique")
    return inverted


def gradebook(names, scores):
    """Return a dict name -> score. Raise ValueError if the lengths differ."""
    # strict=True turns a silent cut-off into a loud ValueError.
    return dict(zip(names, scores, strict=True))


def passed(book, threshold=50):
    """Return the names with a score of at least threshold, sorted alphabetically."""
    # sorted() accepts any iterable, so a generator expression is enough here.
    return sorted(name for name, score in book.items() if score >= threshold)


def all_passed(book, threshold=50):
    """Return True if every score is at least threshold (True for an empty book)."""
    # all() stops at the first failing score and returns True for "nothing to check".
    return all(score >= threshold for score in book.values())


def flatten(grid):
    """Return all values of a list of lists, row by row, as one list."""
    # Two `for`s in the same order as nested loops: outer (rows) first.
    return [value for row in grid for value in row]


def transpose(grid):
    """Return the columns of grid as a list of lists."""
    # zip(*grid) passes every row as a separate argument; zip then yields the columns.
    return [list(column) for column in zip(*grid)]


if __name__ == "__main__":
    book = gradebook(clean_names(["  ada ", "grace", "linus "]), [91, 78, 45])
    print("Gradebook:", book)
    print("Passed:   ", passed(book))
    print("All passed?", all_passed(book))
