from fastapi import HTTPException, status

from app.models import User
from app.repositories import UserRepo
from app.schemas import (
    CreateUserSchema,
    UserSchema,
    UserWithAccountSchema,
    UpdateUserSchema
)
from app.utils.passwords import make_password


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo: UserRepo = repo

    async def __get_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user

    async def get_user(self, user_id: int) -> UserSchema:
        return UserSchema.model_validate(
            await self.__get_user(user_id),
            from_attributes=True
        )

    async def create_user(self, user_data: CreateUserSchema) -> UserSchema:
        existed_user = await self.repo.get_by_email(user_data.email)
        if existed_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email {user_data.email} already exists"
            )

        password_hash = make_password(user_data.password.get_secret_value())
        new_user = User(
            first_name=user_data.first_name,
            surname=user_data.surname,
            last_name=user_data.last_name,
            email=user_data.email,
            password_hash=password_hash
        )
        new_user = await self.repo.create_user(new_user)
        await self.repo.commit()

        return UserSchema.model_validate(new_user, from_attributes=True)

    async def update_user(self, user_id: int, user_data: UpdateUserSchema):
        user = await self.__get_user(user_id)

        if user_data.password is not None:
            user.password_hash = make_password(user_data.password.get_secret_value())
            user_data.password = None

        for field, value in user_data:
            if value is not None:
                setattr(user, field, value)

        await self.repo.commit()

        return UserSchema.model_validate(user, from_attributes=True)

    async def delete_user(self, user_id: int):
        result = await self.repo.delete_by_id(user_id)
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    async def get_users_with_accounts(self):
        users = await self.repo.get_users_with_accounts()
        return [UserWithAccountSchema.model_validate(u, from_attributes=True) for u in users]
