"""Assignment 03 · Bank account.

Replace each `raise NotImplementedError` with your code.
Check your work:  pytest intermediate/03-classes-and-objects/assignments/03-bank-account -v
"""


class BankAccount:
    """A bank account whose balance can never become negative."""

    next_number = 1

    def __init__(self, owner, balance=0):
        """Validate owner and balance, assign a unique number, start an empty history."""
        raise NotImplementedError

    @property
    def owner(self):
        """The owner's name."""
        raise NotImplementedError

    @owner.setter
    def owner(self, value):
        """Store the stripped name; raise ValueError("owner must not be empty") if blank."""
        raise NotImplementedError

    @property
    def balance(self):
        """The current balance (read-only)."""
        raise NotImplementedError

    @property
    def history(self):
        """A copy of the list of (kind, amount) tuples, oldest first."""
        raise NotImplementedError

    def deposit(self, amount):
        """Add amount, record ('deposit', amount), return the new balance."""
        raise NotImplementedError

    def withdraw(self, amount):
        """Subtract amount, record ('withdraw', amount), return the new balance.

        Raise ValueError("insufficient funds") if amount is larger than the balance.
        """
        raise NotImplementedError

    def transfer_to(self, other, amount):
        """Move amount from this account to other."""
        raise NotImplementedError

    @classmethod
    def from_string(cls, text):
        """Create an account from text like 'Ada: 100.5'."""
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


if __name__ == "__main__":
    ada = BankAccount("Ada", 100)
    grace = BankAccount.from_string("Grace: 20")
    ada.transfer_to(grace, 30)
    print(ada)
    print(grace)
    print(ada.history)
