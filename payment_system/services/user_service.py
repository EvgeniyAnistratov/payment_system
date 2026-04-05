from fastapi import HTTPException, status

from payment_system.repositories.user_repo import UserRepo
from payment_system.schemas.user import UserSchema


class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def get_user(self, id: int) -> dict:
        user = await self.user_repo.get_by_id(id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return UserSchema.model_validate(user, from_attributes=True)
