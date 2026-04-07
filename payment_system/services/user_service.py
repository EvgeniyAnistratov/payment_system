from fastapi import HTTPException, status

from payment_system.repositories.user_repo import UserRepo
from payment_system.schemes.user_schemes import UserScheme


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo: UserRepo = repo

    async def get_user(self, user_id: int) -> UserScheme:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return UserScheme.model_validate(user, from_attributes=True)
