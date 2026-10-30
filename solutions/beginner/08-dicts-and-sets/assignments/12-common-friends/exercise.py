"""Assignment 12 · Common friends: template solution."""


def friends_of(network, person):
    """Return person's friends, or an empty set if they have no entry."""
    # A small helper used by every function below: one place handles missing people.
    return network.get(person, set())


def mutual_friends(network, a, b):
    """Return the set of people both a and b list as friends."""
    # & builds a NEW set, so the sets inside network stay untouched.
    return friends_of(network, a) & friends_of(network, b)


def suggestions(network, person):
    """Return friends of person's friends who are not person and not already their friends."""
    own = friends_of(network, person)
    candidates = set()                      # a new set: never update a set from `network`
    for friend in own:
        candidates |= friends_of(network, friend)
    # One difference removes both groups; {person} is a one-item set.
    return candidates - own - {person}


def everyone(network):
    """Return the set of all names: the keys and everyone listed as a friend."""
    names = set(network)                    # set(dict) gives the keys
    for friends in network.values():
        names |= friends                    # names is our own set, so updating it is safe
    return names


def is_mutual(network):
    """Return True if every friendship in the network goes both ways."""
    for person, friends in network.items():
        for friend in friends:
            if person not in friends_of(network, friend):
                return False                # one counter-example is enough
    # Only after checking every pair do we know there is no one-sided friendship.
    return True


if __name__ == "__main__":
    network = {
        "ada": {"grace", "linus", "guido"},
        "grace": {"ada", "guido", "ken"},
        "linus": {"ada"},
        "guido": {"ada", "grace"},
        "ken": {"grace", "barbara"},
    }
    print("Suggestions for linus:", sorted(suggestions(network, "linus")))
