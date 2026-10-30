"""Assignment 11 · Word counter.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/08-dicts-and-sets/assignments/11-word-counter -v
"""

PUNCTUATION = ".,!?;:\"'()"


def words(text):
    """Return the lower-case words of text, with PUNCTUATION stripped from both ends and empties dropped."""
    raise NotImplementedError


def word_counts(text):
    """Return a dict mapping each word to how often it appears."""
    raise NotImplementedError


def most_common(text, n):
    """Return the n most frequent (word, count) tuples, most frequent first, ties alphabetical."""
    raise NotImplementedError


def group_by_length(text):
    """Return a dict mapping word length to a sorted list of the distinct words with that length."""
    raise NotImplementedError


if __name__ == "__main__":
    sample = "It was the best of times, it was the worst of times, it was the age of wisdom."
    for word, count in most_common(sample, 5):
        print(f"{word:<8}{count:>3}")
