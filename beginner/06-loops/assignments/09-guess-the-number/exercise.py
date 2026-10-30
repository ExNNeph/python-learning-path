"""Assignment 09 · Guess the number.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest beginner/06-loops/assignments/09-guess-the-number -v
"""

import random


def hint(guess, secret):
    """Return 'too low', 'too high' or 'correct'."""
    raise NotImplementedError


def play(secret, max_tries=7):
    """Run one game and return the number of tries used, or None if the player failed.

    - Prompt with 'Your guess: ' until correct or max_tries valid guesses are used.
    - Invalid input (not a whole number): print 'Please enter a whole number.' (does not count).
    - After each valid guess, print the hint.
    - On success print 'You got it in <n> tries!' ('try' for 1) and return n.
    - Otherwise print 'Out of tries. The number was <secret>.' and return None.
    """
    raise NotImplementedError


def main():
    print("I am thinking of a number from 1 to 100.")
    play(random.randint(1, 100))


if __name__ == "__main__":
    main()
