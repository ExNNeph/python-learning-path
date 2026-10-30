"""Assignment 11 · Word counter: template solution."""

PUNCTUATION = ".,!?;:\"'()"


def words(text):
    """Return the lower-case words of text, with PUNCTUATION stripped from both ends and empties dropped."""
    # Lower-casing first makes "The" and "the" the same word everywhere below.
    # strip() only touches the ends, so "don't" keeps its apostrophe.
    result = []
    for piece in text.lower().split():
        word = piece.strip(PUNCTUATION)
        if word:                       # "!" or "--" would leave an empty string
            result.append(word)
    return result


def word_counts(text):
    """Return a dict mapping each word to how often it appears."""
    # The counting pattern: get(word, 0) handles the first time a word is seen.
    counts = {}
    for word in words(text):
        counts[word] = counts.get(word, 0) + 1
    return counts


def most_common(text, n):
    """Return the n most frequent (word, count) tuples, most frequent first, ties alphabetical."""
    # Sorting by a tuple compares the first parts, and only on a tie the second parts.
    # -count turns "largest first" into an ascending sort, so one sorted() call
    # handles both directions. (reverse=True would also reverse the alphabetical tie-break.)
    ranked = sorted(word_counts(text).items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:n]


def group_by_length(text):
    """Return a dict mapping word length to a sorted list of the distinct words with that length."""
    groups = {}
    # The dict's keys are the distinct words, so no word is added twice.
    for word in word_counts(text):
        length = len(word)
        if length not in groups:
            groups[length] = []
        groups[length].append(word)
    # Sort at the end, once per group, instead of keeping every list sorted while adding.
    for length in groups:
        groups[length].sort()
    return groups


if __name__ == "__main__":
    sample = "It was the best of times, it was the worst of times, it was the age of wisdom."
    for word, count in most_common(sample, 5):
        print(f"{word:<8}{count:>3}")
