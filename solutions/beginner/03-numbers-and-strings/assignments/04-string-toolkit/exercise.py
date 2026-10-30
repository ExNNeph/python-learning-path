"""Assignment 04 · String toolkit: template solution."""


def initials(full_name):
    """Return the initials of a two-word name: 'ada lovelace' -> 'A.L.'."""
    # split() returns a list of the words; unpacking gives each one a name.
    # If the name had more or fewer than two words, unpacking would raise a ValueError,
    # which is fine: the docstring promises exactly two words.
    first, last = full_name.split()
    return first[0].upper() + "." + last[0].upper() + "."


def is_palindrome(text):
    """Return True if text reads the same backwards, ignoring case and spaces."""
    # Normalise first, compare second: that order keeps the comparison trivial.
    cleaned = text.replace(" ", "").lower()
    # A comparison already produces a bool, so `if ...: return True else: return False`
    # would only add lines.
    return cleaned == cleaned[::-1]


def slugify(title):
    """Return a URL slug: '  Hello   World  ' -> 'hello-world'."""
    # split() with no argument handles leading, trailing and repeated spaces in one go;
    # split(" ") would leave empty strings for every extra space.
    return "-".join(title.lower().split())


def file_extension(filename):
    """Return the part after the last dot: 'report.final.pdf' -> 'pdf'."""
    # rfind searches from the right, so 'archive.tar.gz' gives 'gz', not 'tar.gz'.
    # The slice starts one character after the dot and runs to the end.
    return filename[filename.rfind(".") + 1:]


def mask_card_number(number):
    """Return the number with all but the last 4 characters replaced by '*'."""
    # Multiplying a string repeats it; the count adapts to any length.
    return "*" * (len(number) - 4) + number[-4:]


if __name__ == "__main__":
    print(initials("ada lovelace"), slugify("My First Blog Post"), mask_card_number("4111111111111111"))
