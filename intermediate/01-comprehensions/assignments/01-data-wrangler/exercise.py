"""Assignment 01 · Data wrangler.

Replace each `raise NotImplementedError` with ONE return statement using a comprehension.
Check your work:  pytest intermediate/01-comprehensions/assignments/01-data-wrangler -v
"""


def positive_squares(numbers):
    """Return a list of the squares of the numbers greater than 0, in order."""
    raise NotImplementedError


def clean_names(raw):
    """Return the stripped, title-cased names; drop empty and blank entries."""
    raise NotImplementedError


def email_domains(emails):
    """Return the set of lower-cased domains (the part after '@')."""
    raise NotImplementedError


def word_lengths(words):
    """Return a dict mapping each word to its length."""
    raise NotImplementedError


def invert(mapping):
    """Return a dict with keys and values swapped.

    Raise ValueError("values are not unique") if two keys share a value.
    """
    raise NotImplementedError


def gradebook(names, scores):
    """Return a dict name -> score. Raise ValueError if the lengths differ."""
    raise NotImplementedError


def passed(book, threshold=50):
    """Return the names with a score of at least threshold, sorted alphabetically."""
    raise NotImplementedError


def all_passed(book, threshold=50):
    """Return True if every score is at least threshold (True for an empty book)."""
    raise NotImplementedError


def flatten(grid):
    """Return all values of a list of lists, row by row, as one list."""
    raise NotImplementedError


def transpose(grid):
    """Return the columns of grid as a list of lists."""
    raise NotImplementedError


if __name__ == "__main__":
    book = gradebook(clean_names(["  ada ", "grace", "linus "]), [91, 78, 45])
    print("Gradebook:", book)
    print("Passed:   ", passed(book))
    print("All passed?", all_passed(book))
