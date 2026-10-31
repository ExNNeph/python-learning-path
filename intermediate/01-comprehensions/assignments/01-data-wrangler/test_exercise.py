"""Tests for assignment 01. Run: pytest intermediate/01-comprehensions/assignments/01-data-wrangler -v"""

import pytest


def test_positive_squares(ex):
    assert ex.positive_squares([3, -1, 0, 2]) == [9, 4]
    assert ex.positive_squares([]) == []
    assert ex.positive_squares([-3, 0]) == []


def test_clean_names(ex):
    assert ex.clean_names(["  ada lovelace ", "", "GRACE hopper", "   "]) == ["Ada Lovelace", "Grace Hopper"]


def test_clean_names_keeps_order_and_duplicates(ex):
    assert ex.clean_names(["ken", " linus", "ken"]) == ["Ken", "Linus", "Ken"]


def test_email_domains(ex):
    emails = ["ada@Example.com", "grace@navy.mil", "linus@example.COM"]
    assert ex.email_domains(emails) == {"example.com", "navy.mil"}
    assert ex.email_domains([]) == set()


def test_email_domains_returns_a_set(ex):
    assert isinstance(ex.email_domains(["a@b.c"]), set)


def test_word_lengths(ex):
    assert ex.word_lengths(["apple", "fig", "fig"]) == {"apple": 5, "fig": 3}
    assert ex.word_lengths([]) == {}


def test_invert(ex):
    assert ex.invert({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert ex.invert({}) == {}


def test_invert_does_not_change_the_input(ex):
    mapping = {"a": 1}
    ex.invert(mapping)
    assert mapping == {"a": 1}


def test_invert_duplicate_values(ex):
    with pytest.raises(ValueError, match="values are not unique"):
        ex.invert({"apple": 0.5, "pear": 0.5})


def test_gradebook(ex):
    assert ex.gradebook(["Ada", "Grace"], [91, 78]) == {"Ada": 91, "Grace": 78}
    assert ex.gradebook([], []) == {}


@pytest.mark.parametrize("names, scores", [(["Ada"], [91, 78]), (["Ada", "Grace"], [91])])
def test_gradebook_length_mismatch(ex, names, scores):
    with pytest.raises(ValueError):
        ex.gradebook(names, scores)


def test_passed(ex):
    book = {"Linus": 85, "Ada": 91, "Ken": 42, "Grace": 50}
    assert ex.passed(book) == ["Ada", "Grace", "Linus"]
    assert ex.passed(book, threshold=90) == ["Ada"]
    assert ex.passed({}) == []


def test_all_passed(ex):
    assert ex.all_passed({"Ada": 91, "Grace": 50}) is True
    assert ex.all_passed({"Ada": 91, "Ken": 42}) is False
    assert ex.all_passed({"Ada": 91, "Ken": 42}, threshold=40) is True
    assert ex.all_passed({}) is True


def test_flatten(ex):
    assert ex.flatten([[1, 2, 3], [4, 5, 6]]) == [1, 2, 3, 4, 5, 6]
    assert ex.flatten([[1], [], [2, 3]]) == [1, 2, 3]
    assert ex.flatten([]) == []


def test_transpose(ex):
    assert ex.transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert ex.transpose([[1, 2]]) == [[1], [2]]
    assert ex.transpose([]) == []


def test_transpose_returns_lists(ex):
    assert all(isinstance(row, list) for row in ex.transpose([[1, 2], [3, 4]]))
