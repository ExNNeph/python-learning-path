"""Assignment 01 · First script: template solution."""


def greeting(name):
    """Return 'Hello, <name>! Welcome to Python.'"""
    # `+` joins strings. The spaces and punctuation are part of the strings,
    # so "Hello, " ends with a space and "! Welcome to Python." starts with "!".
    # (Lesson 03 shows a nicer way: f"Hello, {name}! Welcome to Python.")
    return "Hello, " + name + "! Welcome to Python."


def seconds_in_days(days):
    """Return the number of seconds in `days` days."""
    # Writing 24 * 60 * 60 instead of 86400 documents where the number comes from.
    # Python computes the constant part once, while compiling (see `dis` in lesson 01).
    return days * 24 * 60 * 60


def main():
    """Print the greeting for "World", then the number of seconds in a week."""
    # main() *uses* the functions above instead of repeating their logic.
    # The functions return values; only main() decides to print them.
    print(greeting("World"))
    # print() with several arguments separates them with one space.
    print("A week has", seconds_in_days(7), "seconds.")


if __name__ == "__main__":
    main()
