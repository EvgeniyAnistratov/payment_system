from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status

from src.application.use_cases.accounts.list_user_accounts import ListUserAccountsUseCase
from src.application.use_cases.payments.list_user_payments import ListUserPaymentsUseCase
from src.application.use_cases.users.create_user import CreateUserUseCase
from src.application.use_cases.users.delete_user import DeleteUserUseCase
from src.application.use_cases.users.get_user import GetUserUseCase
from src.application.use_cases.users.list_users_with_accounts import ListUsersWithAccountsUseCase
from src.application.use_cases.users.update_user import UpdateUserUseCase
from src.presentation.dependencies.auth import CurrentActor
from src.presentation.schemas.account import AccountResponse
from src.presentation.schemas.payment import PaymentResponse
from src.presentation.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    UserWithAccountsResponse,
)

user_router = APIRouter(route_class=DishkaRoute, prefix="/users", tags=["users"])


@user_router.get("", response_model=list[UserWithAccountsResponse])
async def get_all_users_with_accounts(
    actor: CurrentActor,
    use_case: FromDishka[ListUsersWithAccountsUseCase],
) -> list[UserWithAccountsResponse]:
    users = await use_case.execute(actor)
    return [UserWithAccountsResponse.from_output(user) for user in users]


@user_router.post("", response_model=UserResponse)
async def create_user(
    body: CreateUserRequest,
    actor: CurrentActor,
    use_case: FromDishka[CreateUserUseCase],
) -> UserResponse:
    created = await use_case.execute(actor, body.to_input())
    return UserResponse.from_output(created)


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    actor: CurrentActor,
    use_case: FromDishka[DeleteUserUseCase],
) -> Response:
    await use_case.execute(actor, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UpdateUserRequest,
    actor: CurrentActor,
    use_case: FromDishka[UpdateUserUseCase],
) -> UserResponse:
    updated = await use_case.execute(actor, user_id, body.to_input())
    return UserResponse.from_output(updated)


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user_info(
    user_id: int,
    actor: CurrentActor,
    use_case: FromDishka[GetUserUseCase],
) -> UserResponse:
    user = await use_case.execute(actor, user_id)
    return UserResponse.from_output(user)


@user_router.get("/{user_id}/accounts", response_model=list[AccountResponse])
async def get_user_accounts(
    user_id: int,
    actor: CurrentActor,
    use_case: FromDishka[ListUserAccountsUseCase],
) -> list[AccountResponse]:
    accounts = await use_case.execute(actor, user_id)
    return [AccountResponse.from_output(account) for account in accounts]


@user_router.get("/{user_id}/transactions", response_model=list[PaymentResponse])
async def get_user_transactions(
    user_id: int,
    actor: CurrentActor,
    use_case: FromDishka[ListUserPaymentsUseCase],
) -> list[PaymentResponse]:
    payments = await use_case.execute(actor, user_id)
    return [PaymentResponse.from_output(payment) for payment in payments]
