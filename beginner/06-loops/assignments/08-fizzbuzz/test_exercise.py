"""Tests for assignment 08. Run: pytest beginner/06-loops/assignments/08-fizzbuzz -v"""

import pytest


@pytest.mark.parametrize(
    "n, expected",
    [(1, "1"), (3, "Fizz"), (5, "Buzz"), (9, "Fizz"), (10, "Buzz"), (15, "FizzBuzz"), (30, "FizzBuzz"), (7, "7")],
)
def test_fizzbuzz_word(ex, n, expected):
    assert ex.fizzbuzz_word(n) == expected


def test_fizzbuzz_five(ex):
    assert ex.fizzbuzz(5) == "1\n2\nFizz\n4\nBuzz"


def test_fizzbuzz_fifteen_ends_with_fizzbuzz(ex):
    lines = ex.fizzbuzz(15).split("\n")
    assert len(lines) == 15
    assert lines[-1] == "FizzBuzz"


def test_fizzbuzz_has_no_trailing_newline(ex):
    assert not ex.fizzbuzz(3).endswith("\n")


def test_fizzbuzz_one(ex):
    assert ex.fizzbuzz(1) == "1"


@pytest.mark.parametrize("text, expected", [("Hello World", 3), ("AEIOU", 5), ("rhythm", 0), ("", 0), ("Python is fun", 3)])
def test_count_vowels(ex, text, expected):
    assert ex.count_vowels(text) == expected


@pytest.mark.parametrize("n, expected", [(4096, 19), (0, 0), (7, 7), (1000, 1), (99999, 45)])
def test_sum_of_digits(ex, n, expected):
    assert ex.sum_of_digits(n) == expected


@pytest.mark.parametrize("n, expected", [(0, 1), (1, 1), (5, 120), (10, 3628800)])
def test_factorial(ex, n, expected):
    assert ex.factorial(n) == expected
