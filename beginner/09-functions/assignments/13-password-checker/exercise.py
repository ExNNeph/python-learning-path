"""Assignment 13 · Password checker.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/09-functions/assignments/13-password-checker -v
"""


def has_digit(text):
    """Return True if text contains at least one digit."""
    raise NotImplementedError


def has_upper(text):
    """Return True if text contains at least one uppercase letter."""
    raise NotImplementedError


def has_lower(text):
    """Return True if text contains at least one lowercase letter."""
    raise NotImplementedError


def has_special(text):
    """Return True if text contains at least one character that is not a letter or digit."""
    raise NotImplementedError


def password_problems(password, min_length=8):
    """Return a new list of the problems, in this order:

    'at least <min_length> characters', 'a digit', 'an uppercase letter',
    'a lowercase letter', 'a special character'
    """
    raise NotImplementedError


def strength(password, min_length=8):
    """Return 'strong' (0 problems), 'medium' (1-2) or 'weak' (3+)."""
    raise NotImplementedError


def check_all(passwords, min_length=8):
    """Return a dict mapping each password to its strength."""
    raise NotImplementedError


if __name__ == "__main__":
    password = input("Password to check: ")
    problems = password_problems(password)
    print("Strength:", strength(password))
    for problem in problems:
        print(" - missing:", problem)
