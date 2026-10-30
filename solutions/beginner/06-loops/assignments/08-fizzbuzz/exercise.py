"""Assignment 08 · FizzBuzz and friends: template solution."""


def fizzbuzz_word(n):
    """Return 'FizzBuzz' (divisible by 3 and 5), 'Fizz' (by 3), 'Buzz' (by 5) or str(n)."""
    # The combined case must come first; otherwise 15 would stop at "Fizz".
    # n % 15 == 0 is the same as "divisible by 3 and by 5" because 3 and 5 share no factor.
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


def fizzbuzz(n):
    """Return the FizzBuzz words for 1..n, one per line, joined with '\\n' (no trailing newline)."""
    # Accumulator for text. The separator goes *before* each word except the first,
    # so there is never a newline at the end.
    result = ""
    for i in range(1, n + 1):          # n + 1 because range excludes the stop value
        if result:                     # truthiness: "" is falsy, so this skips the first word
            result += "\n"
        result += fizzbuzz_word(i)
    return result
    # After lesson 07 you can write it in one line:
    # return "\n".join(fizzbuzz_word(i) for i in range(1, n + 1))


def count_vowels(text):
    """Return the number of vowels (a, e, i, o, u; any case) in text."""
    count = 0
    # Lower-casing once, before the loop, means one comparison set instead of two.
    for char in text.lower():
        if char in "aeiou":
            count += 1
    return count


def sum_of_digits(n):
    """Return the sum of the digits of the non-negative int n, using % and //: 4096 -> 19."""
    # while, not for: the number of digits is not known in advance.
    # Each round takes the last digit off; the loop ends when nothing is left.
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    return total


def factorial(n):
    """Return n! = 1 * 2 * ... * n, with factorial(0) == 1."""
    # Start at 1, the neutral element of multiplication (0 would make everything 0).
    result = 1
    for i in range(2, n + 1):          # multiplying by 1 changes nothing, so start at 2
        result *= i
    return result


if __name__ == "__main__":
    print(fizzbuzz(15))
