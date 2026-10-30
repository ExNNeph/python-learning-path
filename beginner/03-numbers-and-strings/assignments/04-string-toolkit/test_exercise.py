"""Tests for assignment 04. Run: pytest beginner/03-numbers-and-strings/assignments/04-string-toolkit -v"""

import pytest


@pytest.mark.parametrize("name, expected", [("ada lovelace", "A.L."), ("Grace Hopper", "G.H."), ("guido van", "G.V.")])
def test_initials(ex, name, expected):
    assert ex.initials(name) == expected


@pytest.mark.parametrize("text", ["racecar", "Racecar", "Never odd or even", "a", ""])
def test_is_palindrome_true(ex, text):
    assert ex.is_palindrome(text) is True


@pytest.mark.parametrize("text", ["Python", "ab", "Hello olleh!"])
def test_is_palindrome_false(ex, text):
    assert ex.is_palindrome(text) is False


@pytest.mark.parametrize(
    "title, expected",
    [("Hello World", "hello-world"), ("  Hello   World  ", "hello-world"), ("Python", "python"), ("My First Blog Post", "my-first-blog-post")],
)
def test_slugify(ex, title, expected):
    assert ex.slugify(title) == expected


@pytest.mark.parametrize(
    "filename, expected",
    [("report.pdf", "pdf"), ("report.final.pdf", "pdf"), ("archive.tar.gz", "gz"), (".gitignore", "gitignore")],
)
def test_file_extension(ex, filename, expected):
    assert ex.file_extension(filename) == expected


@pytest.mark.parametrize(
    "number, expected",
    [("1234567812345678", "************5678"), ("12345", "*2345"), ("1234", "1234")],
)
def test_mask_card_number(ex, number, expected):
    assert ex.mask_card_number(number) == expected
