"""Assignment 03 · Bank account: template solution."""


class BankAccount:
    """A bank account whose balance can never become negative."""

    # Class attribute: ONE counter shared by all accounts. Each new account takes the
    # current value as its number.
    next_number = 1

    def __init__(self, owner, balance=0):
        """Validate owner and balance, assign a unique number, start an empty history."""
        # Assigning through the property runs the setter, so the owner rule lives in
        # exactly one place.
        self.owner = owner
        if balance < 0:
            raise ValueError("balance must not be negative")
        self._balance = balance
        # Read and update the counter on the CLASS. `self.next_number += 1` would read the
        # class value but write a new instance attribute, and every account would get 1.
        self.number = BankAccount.next_number
        BankAccount.next_number += 1
        self._history = []              # created per instance: never a shared class-level list

    @property
    def owner(self):
        """The owner's name."""
        return self._owner

    @owner.setter
    def owner(self, value):
        """Store the stripped name; raise ValueError if blank."""
        name = value.strip()
        if not name:
            raise ValueError("owner must not be empty")
        self._owner = name

    @property
    def balance(self):
        """The current balance (read-only: there is no setter)."""
        return self._balance

    @property
    def history(self):
        """A copy of the list of (kind, amount) tuples, oldest first."""
        # A copy, so callers cannot rewrite the account's history by mutating the list.
        return list(self._history)

    @staticmethod
    def _check_amount(amount):
        # Static: the check needs neither the instance nor the class. The underscore says
        # "internal helper, not part of the public interface".
        if amount <= 0:
            raise ValueError("amount must be positive")

    def deposit(self, amount):
        """Add amount, record ('deposit', amount), return the new balance."""
        self._check_amount(amount)
        self._balance += amount
        self._history.append(("deposit", amount))
        return self._balance

    def withdraw(self, amount):
        """Subtract amount, record ('withdraw', amount), return the new balance."""
        self._check_amount(amount)
        # Check everything BEFORE changing anything: a failed withdrawal leaves the
        # account exactly as it was.
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        self._history.append(("withdraw", amount))
        return self._balance

    def transfer_to(self, other, amount):
        """Move amount from this account to other."""
        # withdraw() validates the amount and the funds and raises before anything has
        # changed, so a failed transfer never leaves money "in the air".
        self.withdraw(amount)
        other.deposit(amount)

    @classmethod
    def from_string(cls, text):
        """Create an account from text like 'Ada: 100.5'."""
        # Unpacking raises ValueError for zero or several colons; float() for bad numbers.
        owner, balance = text.split(":")
        # cls instead of BankAccount: a subclass calling from_string gets a subclass instance.
        return cls(owner, float(balance))

    def __repr__(self):
        # !r adds quotes around strings, so the repr looks like the code that creates it.
        return f"BankAccount(owner={self.owner!r}, balance={self.balance!r})"

    def __str__(self):
        return f"#{self.number} {self.owner}: {self.balance:.2f} EUR"


if __name__ == "__main__":
    ada = BankAccount("Ada", 100)
    grace = BankAccount.from_string("Grace: 20")
    ada.transfer_to(grace, 30)
    print(ada)
    print(grace)
    print(ada.history)
