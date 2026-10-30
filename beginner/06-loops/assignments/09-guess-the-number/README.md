# Assignment 09 · Guess the number

> **Lesson:** [06 · Loops](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~1 h

## Goal

Build a complete little game: the computer picks a secret number from 1 to 100, and the player guesses
until they find it or run out of tries. You practise a `while` loop with `break`, counting rounds, and
rejecting invalid input without crashing.

## What to write

| Function | Returns / does |
|---|---|
| `hint(guess, secret)` | `"too low"`, `"too high"` or `"correct"` |
| `play(secret, max_tries=7)` | runs one game (see below) and returns the number of tries used, or `None` if the player did not find the number |

`play` must:

1. Ask with the prompt `"Your guess: "` until the guess is correct or `max_tries` valid guesses were used.
2. If the input is not a whole number (after `.strip()`), print `Please enter a whole number.`
   and ask again. **Invalid input does not count as a try.**
3. After every valid guess, print the hint (`too low`, `too high` or `correct`).
4. On success, print `You got it in <n> tries!` (use `try` instead of `tries` for 1) and return `n`.
5. After `max_tries` wrong guesses, print `Out of tries. The number was <secret>.` and return `None`.

`main()` is written for you: it picks a random secret and calls `play`.

## Example game

```text
$ python exercise.py
I am thinking of a number from 1 to 100.
Your guess: 50
too high
Your guess: twenty
Please enter a whole number.
Your guess: 25
too low
Your guess: 37
correct
You got it in 3 tries!
```

## Hints

<details>
<summary>Hint 1: the loop shape</summary>

Keep a counter `tries = 0`. Loop `while tries < max_tries:`. Inside, read the input. If it is invalid,
print the message and `continue`. Otherwise increase `tries`, print the hint, and `return` if it was correct.
After the loop you know the player failed.
</details>

<details>
<summary>Hint 2: is it a whole number?</summary>

`"42".isdigit()` is `True`, `"twenty".isdigit()` and `"4.2".isdigit()` are `False`. Check before you call `int()`.
(Lesson 10 shows another way: try the conversion and catch the error.)
</details>

<details>
<summary>Hint 3: "try" or "tries"</summary>

A conditional expression picks the word: `"try" if tries == 1 else "tries"`.
</details>

## Check your work

```bash
pytest beginner/06-loops/assignments/09-guess-the-number -v
```

Then play a round:

```bash
python beginner/06-loops/assignments/09-guess-the-number/exercise.py
```

> **Strategy question:** why are 7 tries always enough for 1–100 if you play well? (Hint: what does
> guessing the middle each time do to the range of possible numbers?)

## Done?

Compare with the [template solution](../../../../solutions/beginner/06-loops/assignments/09-guess-the-number/exercise.py),
then tick off assignment 09 in the [progress checklist](../../../../README.md#progress-checklist).
