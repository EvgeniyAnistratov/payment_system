from datetime import UTC, datetime, timedelta

import jwt

from src.infrastructure.config.settings import JwtSettings


class JwtAccessTokenIssuer:
    def __init__(self, settings: JwtSettings) -> None:
        self._settings = settings

    def issue(self, user_id: int) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=self._settings.access_ttl)
        token = jwt.encode(
            {"exp": expires_at, "sub": str(user_id)},
            self._settings.secret_key.get_secret_value(),
            algorithm=self._settings.algorithm,
        )
        if isinstance(token, bytes):
            return token.decode()
        return token
