import pytest

from src.domain.entities.account import Account
from src.domain.errors.account import AccountOwnershipMismatchError
from src.domain.value_objects.money import Money


def test_open_starts_with_zero_balance() -> None:
    account = Account.open(account_id=77, user_id=2)

    assert account.id == 77
    assert account.user_id == 2
    assert account.balance == 0


def test_deposit_adds_the_amount_for_the_owner() -> None:
    account = Account.open(account_id=1, user_id=2)

    account.deposit(Money(25), payer_id=2)
    account.deposit(Money(10), payer_id=2)

    assert account.balance == 35


def test_deposit_rejects_another_users_payment() -> None:
    account = Account(id=1, user_id=2, balance=50)

    with pytest.raises(AccountOwnershipMismatchError) as error:
        account.deposit(Money(100), payer_id=1)

    assert account.balance == 50
    assert error.value.account_id == 1
    assert error.value.payer_id == 1
