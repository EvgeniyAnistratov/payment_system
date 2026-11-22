from src.domain.entities.account import Account
from src.domain.entities.payment import Payment
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from tests.helpers.fakes.store import InMemoryStore


class InMemoryUserRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    async def find_by_id(self, user_id: int) -> User | None:
        return self._store.users.get(user_id)

    async def find_by_email(self, email: Email) -> User | None:
        for user in self._store.users.values():
            if user.email == email:
                return user
        return None

    async def add(self, user: User) -> User:
        user.id = self._store.next_user_id
        self._store.next_user_id += 1
        self._store.users[user.id] = user
        return user

    async def save(self, user: User) -> None:
        if user.id is None:
            raise ValueError("Cannot save a user without id")
        self._store.users[user.id] = user

    async def delete(self, user_id: int) -> bool:
        return self._store.users.pop(user_id, None) is not None


class InMemoryAccountRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    async def list_by_user_id(self, user_id: int) -> list[Account]:
        return [account for account in self._store.accounts.values() if account.user_id == user_id]

    async def add_if_absent(self, account: Account) -> None:
        self._store.accounts.setdefault(account.id, account)

    async def get_for_update(self, account_id: int) -> Account | None:
        return self._store.accounts.get(account_id)

    async def save(self, account: Account) -> None:
        self._store.accounts[account.id] = account


class InMemoryPaymentRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    async def list_by_user_id(self, user_id: int) -> list[Payment]:
        return [
            payment for payment in self._store.payments.values() if payment.user_id == user_id
        ]

    async def add_if_absent(self, payment: Payment) -> bool:
        if payment.external_id in self._store.payments:
            return False
        payment.id = self._store.next_payment_id
        self._store.next_payment_id += 1
        self._store.payments[payment.external_id] = payment
        return True
