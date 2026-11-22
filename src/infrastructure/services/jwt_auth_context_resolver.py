import jwt

from src.application.dtos.auth import AuthContext
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.config.settings import JwtSettings


class JwtAuthContextResolver:
    def __init__(self, settings: JwtSettings, user_repository: UserRepository) -> None:
        self._settings = settings
        self._user_repository = user_repository

    async def resolve(self, token: str) -> AuthContext | None:
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key.get_secret_value(),
                algorithms=[self._settings.algorithm],
            )
        except jwt.InvalidTokenError:
            return None

        subject = payload.get("sub")
        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            return None

        user = await self._user_repository.find_by_id(user_id)
        if user is None or user.id is None:
            return None
        return AuthContext(user_id=user.id, role=user.role)
