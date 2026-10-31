# Assignment 03 · Test the tests

> **Lesson:** [03 · Testing like a professional](../../) · **Difficulty:** ⭐⭐⭐⭐☆ · **Time:** ~2 h

## Goal

Until now, the tests were given and you wrote the code. This time the code is given and **you write the
tests**. [`pricing.py`](pricing.py) calculates the price of a web-shop order. It is correct. Your job is
to write a test suite in `exercise.py` that would catch it if somebody broke it.

How do we know your tests are good? With **mutation testing** (lesson section 7). The checker runs your
tests:

1. against the real `pricing.py`: **all your tests must pass**, and there must be at least 8 of them;
2. against **10 mutants**: copies of `pricing.py`, each with one small planted bug. For every mutant,
   **at least one of your tests must fail**. A mutant that passes all your tests has "survived", and the
   checker tells you its name.

The mutants are the kind of bugs that happen in real code: an off-by-one at a boundary, a wrong rounding,
a forgotten case, a call that should not happen.

## The code under test

Read [`pricing.py`](pricing.py) first: its docstrings are the specification. In short:

| Function | Behaviour |
|---|---|
| `subtotal(items)` | sum of `unit_price * quantity`; a quantity below 1 raises `ValueError` |
| `discount(amount, code)` | `None` → 0; `"SAVE10"` → 10 % rounded down; `"FLAT5"` → 500 from an amount of 2000; codes are case-insensitive; unknown codes raise `ValueError` |
| `shipping(amount)` | free from 5000, else 495 |
| `convert(cents, currency, rates)` | `"EUR"` → unchanged, **without** asking `rates`; else `round(cents * rates.get_rate(currency))` |
| `total(items, code, currency, rates)` | subtotal − discount + shipping (on the discounted amount), converted |

## What to write

Tests in `exercise.py`, as many as you need, using everything from the lesson: boundaries, `parametrize`,
`pytest.raises`, fixtures, and a `Mock` for the rate provider. Replace the five placeholder tests (each
calls `pytest.fail`). The surviving mutant names are hints, so read them when one survives.

## Run them

Run your own tests while writing them (from the assignment folder, so `import pricing` works):

```bash
cd professional/03-testing-like-a-professional/assignments/03-test-the-tests
python -m pytest exercise.py -v
```

Then let the mutants loose, from the repository root:

```bash
pytest professional/03-testing-like-a-professional/assignments/03-test-the-tests -v
```

```text
test_exercise.py::test_your_tests_pass_on_the_real_code PASSED
test_exercise.py::test_your_tests_catch_the_mutant[quantity-zero-allowed] PASSED
test_exercise.py::test_your_tests_catch_the_mutant[shipping-boundary] FAILED
    mutant 'shipping-boundary' survived: no test failed. Which behaviour is not checked?
```

## Hints

<details>
<summary>Hint 1: boundaries</summary>

For every `<`, `>=` and every rounding in `pricing.py`, write a case **exactly at** the limit and one
**just below** it: a quantity of 0, an amount of 1999 and 2000, 4999 and 5000, an amount whose 10 % is not
a whole number.
</details>

<details>
<summary>Hint 2: the mocks</summary>

```python
rates = Mock()
rates.get_rate.return_value = 1.25
```

Check not only the **result** of `convert`, but also **how** `rates` was used:
`rates.get_rate.assert_called_once_with("USD")` and, for euros, `rates.get_rate.assert_not_called()`.
Two of the mutants return the right number and are only visible this way.
</details>

<details>
<summary>Hint 3: total</summary>

One mutant computes shipping on the amount **before** the discount. Find an order where that makes a
difference: one that is above the free-shipping limit before the discount, and below it after.
</details>

## Done?

Compare with the [template solution](../../../../solutions/professional/03-testing-like-a-professional/assignments/03-test-the-tests/exercise.py),
then tick off assignment 03 in the [progress checklist](../../../../README.md#progress-checklist).
