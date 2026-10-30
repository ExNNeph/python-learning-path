"""Assignment 13 · Password checker: template solution."""


# Four tiny helpers instead of one big function: each has one job, a name that reads
# like a question, and can be tested on its own.

def has_digit(text):
    """Return True if text contains at least one digit."""
    for char in text:
        if char.isdigit():
            return True      # found one: no need to look further
    return False             # only after checking every character


def has_upper(text):
    """Return True if text contains at least one uppercase letter."""
    # any() does the loop above for us: True as soon as one item is truthy.
    return any(char.isupper() for char in text)


def has_lower(text):
    """Return True if text contains at least one lowercase letter."""
    return any(char.islower() for char in text)


def has_special(text):
    """Return True if text contains at least one character that is not a letter or digit."""
    return any(not char.isalnum() for char in text)


def password_problems(password, min_length=8):
    """Return a new list of the problems, in this order."""
    # The list is created inside the function, so every call gets a fresh one.
    # `def password_problems(password, min_length=8, problems=[])` would share ONE
    # list between all calls (the mutable default trap).
    problems = []
    if len(password) < min_length:
        problems.append(f"at least {min_length} characters")
    if not has_digit(password):
        problems.append("a digit")
    if not has_upper(password):
        problems.append("an uppercase letter")
    if not has_lower(password):
        problems.append("a lowercase letter")
    if not has_special(password):
        problems.append("a special character")
    return problems


def strength(password, min_length=8):
    """Return 'strong' (0 problems), 'medium' (1-2) or 'weak' (3+)."""
    count = len(password_problems(password, min_length=min_length))
    if count == 0:
        return "strong"
    if count <= 2:
        return "medium"
    return "weak"


def check_all(passwords, min_length=8):
    """Return a dict mapping each password to its strength."""
    # Passing min_length by keyword makes the call robust: if someone later adds a
    # parameter before min_length in strength(), this line still does the right thing.
    return {password: strength(password, min_length=min_length) for password in passwords}


if __name__ == "__main__":
    password = input("Password to check: ")
    problems = password_problems(password)
    print("Strength:", strength(password))
    for problem in problems:
        print(" - missing:", problem)
