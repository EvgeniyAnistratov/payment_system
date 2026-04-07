from typing import Annotated, List

from fastapi import APIRouter, Depends, Response, status
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from app.auth.current_user import get_current_user
from app.auth.permissions import has_role, is_owner_or_admin
from app.constants.enums import Role
from app.models import User
from app.schemas import (
    AccountSchema,
    TransactionSchema,
    CreateUserSchema, UserSchema, UpdateUserSchema, UserWithAccountSchema
)
from app.services import AccountService, TransactionService, UserService


user_router = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["users"])


@user_router.get("", response_model=List[UserWithAccountSchema])
@has_role(Role.ADMIN)
async def get_all_users_with_accounts(
    current_user: Annotated[str, Depends(get_current_user)],
    user_service: FromDishka[UserService]
):
    result = await user_service.get_users_with_accounts()
    return result


@user_router.post("", response_model=UserSchema)
@has_role(Role.ADMIN)
async def create_user(
    user_data: CreateUserSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: FromDishka[UserService]
):
    return await user_service.create_user(user_data)


@user_router.delete("/{user_id}")
@has_role(Role.ADMIN)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: FromDishka[UserService]
):
    await user_service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.patch("/{user_id}", response_model=UserSchema)
@has_role(Role.ADMIN)
async def update_user(
    user_id: int,
    user_data: UpdateUserSchema,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: FromDishka[UserService]
):
    return await user_service.update_user(user_id, user_data)


@user_router.get("/{user_id}", response_model=UserSchema)
@is_owner_or_admin
async def get_user_info(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: FromDishka[UserService]
):
    if current_user.id == user_id:
        return UserSchema.model_validate(current_user, from_attributes=True)

    return await user_service.get_user(user_id)


@user_router.get("/{user_id}/accounts", response_model=List[AccountSchema])
@is_owner_or_admin
async def get_user_accounts(
    user_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
    account_service: FromDishka[AccountService]
):
    return await account_service.get_list_by_user_id(user_id)


@user_router.get("/{user_id}/transactions", response_model=List[TransactionSchema])
@is_owner_or_admin
async def get_user_transactions(
    user_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
    transaction_service: FromDishka[TransactionService]
):
    return await transaction_service.get_list_by_user_id(user_id)
