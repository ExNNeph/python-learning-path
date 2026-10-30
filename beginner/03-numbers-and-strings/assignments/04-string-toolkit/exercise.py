"""Assignment 04 · String toolkit.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/03-numbers-and-strings/assignments/04-string-toolkit -v
"""


def initials(full_name):
    """Return the initials of a two-word name: 'ada lovelace' -> 'A.L.'."""
    raise NotImplementedError


def is_palindrome(text):
    """Return True if text reads the same backwards, ignoring case and spaces."""
    raise NotImplementedError


def slugify(title):
    """Return a URL slug: '  Hello   World  ' -> 'hello-world'."""
    raise NotImplementedError


def file_extension(filename):
    """Return the part after the last dot: 'report.final.pdf' -> 'pdf'."""
    raise NotImplementedError


def mask_card_number(number):
    """Return the number with all but the last 4 characters replaced by '*'."""
    raise NotImplementedError


if __name__ == "__main__":
    print(initials("ada lovelace"), slugify("My First Blog Post"), mask_card_number("4111111111111111"))
