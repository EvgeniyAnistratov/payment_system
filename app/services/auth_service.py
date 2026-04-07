from fastapi import HTTPException, status

from app.repositories.user_repo import UserRepo
from app.utils.passwords import compare_passwords
from app.utils.tokens import get_access_token


class AuthService:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def __init__(self, repo: UserRepo):
        self.user_repo: UserRepo = repo

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise self.credentials_exception

        if not compare_passwords(password, user.password_hash):
            raise self.credentials_exception

        return get_access_token(user.id)
