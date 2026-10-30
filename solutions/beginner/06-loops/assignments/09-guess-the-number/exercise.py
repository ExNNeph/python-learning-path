"""Assignment 09 · Guess the number: template solution."""

import random


def hint(guess, secret):
    """Return 'too low', 'too high' or 'correct'."""
    # Pure function: no input, no print. That makes the game rules testable on their own.
    if guess < secret:
        return "too low"
    if guess > secret:
        return "too high"
    return "correct"


def play(secret, max_tries=7):
    """Run one game and return the number of tries used, or None if the player failed."""
    tries = 0
    # `while`, not `for`: invalid input must not use up a round, so the number of
    # loop rounds is not known in advance. Only valid guesses move `tries` forward.
    while tries < max_tries:
        answer = input("Your guess: ").strip()
        if not answer.isdigit():
            print("Please enter a whole number.")
            continue                      # back to the top, `tries` unchanged

        tries += 1
        result = hint(int(answer), secret)
        print(result)
        if result == "correct":
            word = "try" if tries == 1 else "tries"
            print(f"You got it in {tries} {word}!")
            return tries                  # return also ends the loop

    # Reaching this line means the loop ran out without a correct guess.
    print(f"Out of tries. The number was {secret}.")
    return None


def main():
    print("I am thinking of a number from 1 to 100.")
    play(random.randint(1, 100))


if __name__ == "__main__":
    main()
