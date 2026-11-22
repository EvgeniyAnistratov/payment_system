from dataclasses import dataclass

from src.domain.errors.account import AccountOwnershipMismatchError
from src.domain.errors.base import DomainValidationError
from src.domain.value_objects.money import Money


@dataclass(slots=True)
class Account:
    id: int
    user_id: int
    balance: int

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise DomainValidationError("Account id must be positive")
        if self.user_id <= 0:
            raise DomainValidationError("User id must be positive")
        if self.balance < 0:
            raise DomainValidationError("Balance must not be negative")

    @classmethod
    def open(cls, account_id: int, user_id: int) -> "Account":
        return cls(id=account_id, user_id=user_id, balance=0)

    def deposit(self, amount: Money, payer_id: int) -> None:
        if payer_id != self.user_id:
            raise AccountOwnershipMismatchError(self.id, payer_id)
        self.balance += amount.value
