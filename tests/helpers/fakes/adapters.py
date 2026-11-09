from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from src.application.dtos.payment import ProcessPaymentInput
from src.application.dtos.user import UserWithAccountsOutput
from tests.helpers.fakes.store import InMemoryStore


class FakePasswordHasher:
    async def hash(self, raw_password: str) -> str:
        return f"hashed:{raw_password}"

    async def verify(self, raw_password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{raw_password}"


class FakeAccessTokenIssuer:
    def issue(self, user_id: int) -> str:
        return f"token:{user_id}"


class FakePaymentSignatureVerifier:
    def __init__(self, valid: bool = True) -> None:
        self.valid = valid
        self.checked: list[ProcessPaymentInput] = []

    def verify(self, payment: ProcessPaymentInput) -> bool:
        self.checked.append(payment)
        return self.valid


class FakeTransactionManager:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self.entered = 0
        self.commits = 0
        self.rollbacks = 0

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        self.entered += 1
        self._store.begin()
        try:
            yield
        except BaseException:
            self._store.rollback()
            self.rollbacks += 1
            raise
        self._store.commit()
        self.commits += 1


class InMemoryUsersWithAccountsQuery:
    def __init__(self, rows: list[UserWithAccountsOutput] | None = None) -> None:
        self.rows = list(rows or [])

    async def fetch(self) -> list[UserWithAccountsOutput]:
        return list(self.rows)
