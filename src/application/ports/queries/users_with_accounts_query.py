from typing import Protocol

from src.application.dtos.user import UserWithAccountsOutput


class UsersWithAccountsQuery(Protocol):
    async def fetch(self) -> list[UserWithAccountsOutput]: ...
