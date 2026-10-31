# Assignment 03 · Bank account

> **Lesson:** [03 · Classes and objects](../../) · **Difficulty:** ⭐⭐⭐☆☆ · **Time:** ~2 h

## Goal

Write a `BankAccount` class that **protects its own rules**: the balance can never become negative,
and it can only change through `deposit`, `withdraw` and `transfer_to`. You practise `__init__`,
methods, properties, a class attribute, `__repr__`/`__str__` and a class method.

## What to write

`class BankAccount` with:

| Member | Does |
|---|---|
| `BankAccount(owner, balance=0)` | creates an account. Rules below. Every account gets a unique `number`: the first account created gets the current value of the **class attribute** `next_number` (which starts at `1`), and the class attribute then goes up by 1 |
| `owner` | property with a setter: stores the name **stripped**; an empty or blank name raises `ValueError("owner must not be empty")` (in `__init__` too) |
| `balance` | **read-only** property. A negative starting balance raises `ValueError("balance must not be negative")` |
| `deposit(amount)` | adds `amount`, records `("deposit", amount)` in the history, returns the new balance |
| `withdraw(amount)` | subtracts `amount`, records `("withdraw", amount)`, returns the new balance. More than the balance: `ValueError("insufficient funds")` and **nothing changes** |
| `transfer_to(other, amount)` | moves `amount` from this account to `other` (a withdraw here and a deposit there) |
| `history` | property: a **copy** of the list of `(kind, amount)` tuples, oldest first |
| `__repr__` | `BankAccount(owner='Ada', balance=100)` |
| `__str__` | `#1 Ada: 100.00 EUR` (number, owner, balance with 2 decimals) |
| `from_string(text)` | **class method**: `BankAccount.from_string("Ada: 100.5")` → an account for `Ada` with balance `100.5`. Text without exactly one `:` or with a non-numeric balance raises `ValueError` |

In `deposit`, `withdraw` and `transfer_to`, an amount that is **not greater than 0** raises
`ValueError("amount must be positive")`.

## Examples

```python
>>> ada = BankAccount("  Ada ", 100)
>>> ada
BankAccount(owner='Ada', balance=100)
>>> ada.deposit(50)
150
>>> ada.withdraw(500)
Traceback (most recent call last):
ValueError: insufficient funds
>>> grace = BankAccount.from_string("Grace: 20")
>>> ada.transfer_to(grace, 30)
>>> ada.balance, grace.balance
(120, 50.0)
>>> ada.history
[('deposit', 50), ('withdraw', 30)]
>>> print(ada)
#1 Ada: 120.00 EUR
>>> ada.balance = 10**6
Traceback (most recent call last):
AttributeError: ...
```

### A design question: `__eq__`?

You do **not** need `__eq__` here. Two accounts with the same owner and balance are still two
different accounts, so the default (equal only to itself) is exactly right. Value equality is for
objects that *are* their values, like a point or an amount of money (lesson 05).

## Hints

<details>
<summary>Hint 1: the account number</summary>

Read and increase the class attribute through the class, not through `self`:
`self.number = BankAccount.next_number` and then `BankAccount.next_number += 1`.
`self.next_number += 1` would create a new **instance** attribute and leave the class counter unchanged.
</details>

<details>
<summary>Hint 2: one place for each rule</summary>

Write a small helper `_check_amount(amount)` (a static method or module function) and call it at the
start of `deposit`, `withdraw` and `transfer_to`. In `__init__`, assign `self.owner = owner` so the
property setter does the validation for you.
</details>

<details>
<summary>Hint 3: from_string</summary>

`owner, balance = text.split(":")` raises `ValueError` by itself if there is not exactly one colon,
and so does `float("abc")`. Then `return cls(owner, float(balance))`.
</details>

## Check your work

```bash
pytest intermediate/03-classes-and-objects/assignments/03-bank-account -v
```

## Done?

Compare with the [template solution](../../../../solutions/intermediate/03-classes-and-objects/assignments/03-bank-account/exercise.py),
then tick off assignment 03 in the [progress checklist](../../../../README.md#progress-checklist).
