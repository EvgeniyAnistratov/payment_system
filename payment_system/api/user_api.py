from typing import List

from fastapi import APIRouter
from dishka.integrations.fastapi import DishkaRoute, FromDishka

from payment_system.schemas import AccountSchema, TransactionSchema, UserSchema
from payment_system.services import AccountService, TransactionService, UserService


user_router = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserSchema)
async def get_user_info(user_id: int, user_service: FromDishka[UserService]):
    return await user_service.get_user(user_id)


@user_router.get("/{user_id}/accounts", response_model=List[AccountSchema])
async def get_user_accounts(user_id: int, account_service: FromDishka[AccountService]):
    return await account_service.get_list_by_user_id(user_id)


@user_router.get("/{user_id}/transactions", response_model=List[TransactionSchema])
async def get_user_transactions(user_id: int, transaction_service: FromDishka[TransactionService]):
    return await transaction_service.get_list_by_user_id(user_id)
