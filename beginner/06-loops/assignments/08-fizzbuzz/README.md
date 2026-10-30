# Assignment 08 · FizzBuzz and friends

> **Lesson:** [06 · Loops](../../) · **Difficulty:** ⭐⭐☆☆☆ · **Time:** ~45 min

## Goal

Four short loop functions. FizzBuzz is the most famous small programming test in the world: it checks
that you can combine a loop, `%` and conditions in the right order. The others practise the accumulator
pattern and `while`.

## What to write

| Function | Returns |
|---|---|
| `fizzbuzz_word(n)` | `"FizzBuzz"` if `n` is divisible by 3 and 5, `"Fizz"` if by 3, `"Buzz"` if by 5, otherwise the number as a string |
| `fizzbuzz(n)` | the words for 1 to `n`, one per line, joined with `"\n"` (no newline at the end) |
| `count_vowels(text)` | how many vowels (`a e i o u`, upper or lower case) are in `text` |
| `sum_of_digits(n)` | the sum of the digits of a non-negative int, computed with `%` and `//` |
| `factorial(n)` | `n! = 1 × 2 × … × n`, with `factorial(0) == 1` |

## Examples

```python
>>> fizzbuzz_word(9)
'Fizz'
>>> fizzbuzz_word(10)
'Buzz'
>>> fizzbuzz_word(30)
'FizzBuzz'
>>> fizzbuzz_word(7)
'7'
>>> print(fizzbuzz(5))
1
2
Fizz
4
Buzz
>>> count_vowels("Hello World")
3
>>> sum_of_digits(4096)
19
>>> factorial(5)
120
```

## Hints

<details>
<summary>Hint 1: FizzBuzz order</summary>

Which check must come first? A number divisible by 15 is also divisible by 3, so if you check
`% 3` first, you will never reach `"FizzBuzz"`. (Lesson 05: narrowest condition first.)
</details>

<details>
<summary>Hint 2: joining lines without a trailing newline</summary>

One way: build the text in an accumulator and add `"\n"` **before** every word except the first.
Another: add `"\n"` after every word and remove the last one with `.rstrip("\n")` or a slice at the end.
</details>

<details>
<summary>Hint 3: count_vowels</summary>

Loop over the characters of `text.lower()` and count those that are `in "aeiou"`.
</details>

<details>
<summary>Hint 4: sum_of_digits without converting to a string</summary>

`n % 10` is the last digit, `n // 10` drops the last digit. Repeat `while n > 0`.
</details>

<details>
<summary>Hint 5: factorial</summary>

An accumulator that starts at `1` (not 0!) and multiplies by every number in `range(1, n + 1)`.
For `n = 0` the loop does not run at all, and the start value `1` is already the right answer.
</details>

## Check your work

```bash
pytest beginner/06-loops/assignments/08-fizzbuzz -v
```

## Done?

Compare with the [template solution](../../../../solutions/beginner/06-loops/assignments/08-fizzbuzz/exercise.py),
then tick off assignment 08 in the [progress checklist](../../../../README.md#progress-checklist).
