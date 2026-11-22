import copy
from dataclasses import dataclass, field

from src.domain.entities.account import Account
from src.domain.entities.payment import Payment
from src.domain.entities.user import User


@dataclass
class InMemoryStore:
    users: dict[int, User] = field(default_factory=dict)
    accounts: dict[int, Account] = field(default_factory=dict)
    payments: dict[str, Payment] = field(default_factory=dict)
    next_user_id: int = 1
    next_payment_id: int = 1
    _snapshots: list[tuple[object, ...]] = field(default_factory=list)

    def begin(self) -> None:
        self._snapshots.append(
            (
                copy.deepcopy(self.users),
                copy.deepcopy(self.accounts),
                copy.deepcopy(self.payments),
                self.next_user_id,
                self.next_payment_id,
            )
        )

    def rollback(self) -> None:
        users, accounts, payments, next_user_id, next_payment_id = self._snapshots.pop()
        self.users = users
        self.accounts = accounts
        self.payments = payments
        self.next_user_id = next_user_id
        self.next_payment_id = next_payment_id

    def commit(self) -> None:
        self._snapshots.pop()
