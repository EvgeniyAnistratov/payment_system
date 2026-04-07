from typing import Annotated, List

from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from payment_system.auth.current_user import get_current_user
from payment_system.auth.permissions import is_owner_or_admin
from payment_system.models import User
from payment_system.schemes import AccountScheme, TransactionScheme, UserScheme
from payment_system.services import AccountService, TransactionService, UserService


user_router = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserScheme)
@is_owner_or_admin
async def get_user_info(
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: FromDishka[UserService]
):
    if current_user.id == user_id:
        return UserScheme.model_validate(current_user, from_attributes=True)

    return await user_service.get_user(user_id)


@user_router.get("/{user_id}/accounts", response_model=List[AccountScheme])
@is_owner_or_admin
async def get_user_accounts(
    user_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
    account_service: FromDishka[AccountService]
):
    return await account_service.get_list_by_user_id(user_id)


@user_router.get("/{user_id}/transactions", response_model=List[TransactionScheme])
@is_owner_or_admin
async def get_user_transactions(
    user_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
    transaction_service: FromDishka[TransactionService]
):
    return await transaction_service.get_list_by_user_id(user_id)
