from typing import Annotated

from fastapi import APIRouter, Depends
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi.security import OAuth2PasswordRequestForm

from payment_system.schemas import Token
from payment_system.services import AuthService


auth_router = APIRouter(route_class=DishkaRoute, prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=Token)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: FromDishka[AuthService]
):
    access_token = await auth_service.login(form_data.username, form_data.password)
    return Token(access_token=access_token, token_type="bearer")
