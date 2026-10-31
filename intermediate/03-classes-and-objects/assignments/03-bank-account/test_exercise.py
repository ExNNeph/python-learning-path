"""Tests for assignment 03. Run: pytest intermediate/03-classes-and-objects/assignments/03-bank-account -v"""

import pytest


@pytest.fixture
def Account(ex):
    return ex.BankAccount


def test_create(Account):
    account = Account("Ada", 100)
    assert account.owner == "Ada"
    assert account.balance == 100


def test_default_balance(Account):
    assert Account("Ada").balance == 0


def test_owner_is_stripped(Account):
    assert Account("  Ada ").owner == "Ada"


@pytest.mark.parametrize("owner", ["", "   "])
def test_blank_owner(Account, owner):
    with pytest.raises(ValueError, match="owner must not be empty"):
        Account(owner)


def test_owner_setter_validates(Account):
    account = Account("Ada")
    account.owner = " Ada Lovelace "
    assert account.owner == "Ada Lovelace"
    with pytest.raises(ValueError):
        account.owner = " "
    assert account.owner == "Ada Lovelace"


def test_negative_start_balance(Account):
    with pytest.raises(ValueError, match="balance must not be negative"):
        Account("Ada", -1)


def test_balance_is_read_only(Account):
    account = Account("Ada", 100)
    with pytest.raises(AttributeError):
        account.balance = 10**6
    assert account.balance == 100


def test_numbers_are_unique_and_increasing(Account):
    first, second = Account("Ada"), Account("Grace")
    assert second.number == first.number + 1
    assert Account.next_number == second.number + 1


def test_next_number_lives_on_the_class(Account):
    account = Account("Ada")
    assert "next_number" not in vars(account)


def test_deposit(Account):
    account = Account("Ada", 100)
    assert account.deposit(50) == 150
    assert account.balance == 150


def test_withdraw(Account):
    account = Account("Ada", 100)
    assert account.withdraw(30) == 70
    assert account.withdraw(70) == 0


def test_withdraw_too_much_changes_nothing(Account):
    account = Account("Ada", 100)
    with pytest.raises(ValueError, match="insufficient funds"):
        account.withdraw(100.01)
    assert account.balance == 100
    assert account.history == []


@pytest.mark.parametrize("method", ["deposit", "withdraw"])
@pytest.mark.parametrize("amount", [0, -5])
def test_amount_must_be_positive(Account, method, amount):
    account = Account("Ada", 100)
    with pytest.raises(ValueError, match="amount must be positive"):
        getattr(account, method)(amount)
    assert account.balance == 100


def test_transfer(Account):
    ada, grace = Account("Ada", 100), Account("Grace", 20)
    ada.transfer_to(grace, 30)
    assert (ada.balance, grace.balance) == (70, 50)
    assert ada.history == [("withdraw", 30)]
    assert grace.history == [("deposit", 30)]


def test_failed_transfer_changes_nothing(Account):
    ada, grace = Account("Ada", 10), Account("Grace", 20)
    with pytest.raises(ValueError):
        ada.transfer_to(grace, 30)
    with pytest.raises(ValueError):
        ada.transfer_to(grace, -5)
    assert (ada.balance, grace.balance) == (10, 20)
    assert grace.history == []


def test_history_order(Account):
    account = Account("Ada", 100)
    account.deposit(50)
    account.withdraw(30)
    assert account.history == [("deposit", 50), ("withdraw", 30)]


def test_history_is_a_copy(Account):
    account = Account("Ada", 100)
    account.deposit(5)
    account.history.append(("deposit", 10**6))
    account.history.clear()
    assert account.history == [("deposit", 5)]


def test_histories_are_separate(Account):
    ada, grace = Account("Ada", 100), Account("Grace", 100)
    ada.deposit(1)
    assert grace.history == []


def test_repr(Account):
    assert repr(Account("Ada", 100)) == "BankAccount(owner='Ada', balance=100)"


def test_str(Account):
    account = Account("Ada", 120)
    assert str(account) == f"#{account.number} Ada: 120.00 EUR"


def test_from_string(Account):
    account = Account.from_string("Grace: 20.5")
    assert isinstance(account, Account)
    assert (account.owner, account.balance) == ("Grace", 20.5)


@pytest.mark.parametrize("text", ["Grace 20", "a:b:1", "Grace: lots", ": 5", "Grace: -1"])
def test_from_string_invalid(Account, text):
    with pytest.raises(ValueError):
        Account.from_string(text)


def test_from_string_uses_cls(Account):
    class SavingsAccount(Account):
        pass

    assert type(SavingsAccount.from_string("Ada: 1")) is SavingsAccount
