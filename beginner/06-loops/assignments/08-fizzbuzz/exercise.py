"""Assignment 08 · FizzBuzz and friends.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/06-loops/assignments/08-fizzbuzz -v
"""


def fizzbuzz_word(n):
    """Return 'FizzBuzz' (divisible by 3 and 5), 'Fizz' (by 3), 'Buzz' (by 5) or str(n)."""
    raise NotImplementedError


def fizzbuzz(n):
    """Return the FizzBuzz words for 1..n, one per line, joined with '\\n' (no trailing newline)."""
    raise NotImplementedError


def count_vowels(text):
    """Return the number of vowels (a, e, i, o, u; any case) in text."""
    raise NotImplementedError


def sum_of_digits(n):
    """Return the sum of the digits of the non-negative int n, using % and //: 4096 -> 19."""
    raise NotImplementedError


def factorial(n):
    """Return n! = 1 * 2 * ... * n, with factorial(0) == 1."""
    raise NotImplementedError


if __name__ == "__main__":
    print(fizzbuzz(15))
