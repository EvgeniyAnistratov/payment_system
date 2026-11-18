from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.application.dtos.auth import SignInInput
from src.application.use_cases.auth.sign_in import SignInUseCase
from src.presentation.schemas.auth import TokenResponse

auth_router = APIRouter(route_class=DishkaRoute, prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=TokenResponse)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: FromDishka[SignInUseCase],
) -> TokenResponse:
    token = await use_case.execute(
        SignInInput(email=form_data.username, password=form_data.password)
    )
    return TokenResponse.from_output(token)
