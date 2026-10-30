"""Assignment 12 · Common friends.

Replace each `raise NotImplementedError` with your code. Do not change `network`.
Check your work:  pytest beginner/08-dicts-and-sets/assignments/12-common-friends -v
"""


def mutual_friends(network, a, b):
    """Return the set of people both a and b list as friends."""
    raise NotImplementedError


def suggestions(network, person):
    """Return friends of person's friends who are not person and not already their friends."""
    raise NotImplementedError


def everyone(network):
    """Return the set of all names: the keys and everyone listed as a friend."""
    raise NotImplementedError


def is_mutual(network):
    """Return True if every friendship in the network goes both ways."""
    raise NotImplementedError


if __name__ == "__main__":
    network = {
        "ada": {"grace", "linus", "guido"},
        "grace": {"ada", "guido", "ken"},
        "linus": {"ada"},
        "guido": {"ada", "grace"},
        "ken": {"grace", "barbara"},
    }
    print("Suggestions for linus:", sorted(suggestions(network, "linus")))
