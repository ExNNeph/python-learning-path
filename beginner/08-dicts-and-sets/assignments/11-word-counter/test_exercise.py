"""Tests for assignment 11. Run: pytest beginner/08-dicts-and-sets/assignments/11-word-counter -v"""

SAMPLE = "The cat sat. The CAT ran!"


def test_words_lowercase_and_stripped(ex):
    assert ex.words(SAMPLE) == ["the", "cat", "sat", "the", "cat", "ran"]


def test_words_drops_empty_pieces(ex):
    assert ex.words("Hello ! world") == ["hello", "world"]


def test_words_keeps_inner_apostrophe(ex):
    assert ex.words('"Don\'t," she said.') == ["don't", "she", "said"]


def test_words_empty_text(ex):
    assert ex.words("") == []


def test_word_counts(ex):
    assert ex.word_counts(SAMPLE) == {"the": 2, "cat": 2, "sat": 1, "ran": 1}


def test_word_counts_empty(ex):
    assert ex.word_counts("") == {}


def test_most_common_ties_are_alphabetical(ex):
    assert ex.most_common(SAMPLE, 3) == [("cat", 2), ("the", 2), ("ran", 1)]


def test_most_common_n_larger_than_vocabulary(ex):
    assert ex.most_common("b a b", 10) == [("b", 2), ("a", 1)]


def test_most_common_dickens(ex):
    text = "It was the best of times, it was the worst of times, it was the age of wisdom."
    assert ex.most_common(text, 4) == [("it", 3), ("of", 3), ("the", 3), ("was", 3)]


def test_group_by_length(ex):
    assert ex.group_by_length("The cat sat on a mat") == {3: ["cat", "mat", "sat", "the"], 2: ["on"], 1: ["a"]}


def test_group_by_length_has_no_duplicates(ex):
    assert ex.group_by_length("to be or not to be") == {2: ["be", "or", "to"], 3: ["not"]}
