from dataclasses import dataclass

from src.domain.entities.account import Account


@dataclass(frozen=True, slots=True)
class AccountOutput:
    id: int
    user_id: int
    balance: int


def to_account_output(account: Account) -> AccountOutput:
    return AccountOutput(id=account.id, user_id=account.user_id, balance=account.balance)
