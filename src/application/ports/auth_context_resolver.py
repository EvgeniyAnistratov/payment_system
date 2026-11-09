from typing import Protocol

from src.application.dtos.auth import AuthContext


class AuthContextResolver(Protocol):
    async def resolve(self, token: str) -> AuthContext | None: ...
