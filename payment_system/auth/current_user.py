from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from payment_system.core import settings
from payment_system.models import User
from payment_system.repositories import UserRepo
from payment_system.utils.tokens import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.JWT_TOKEN_URL)


@inject
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: FromDishka[UserRepo]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except InvalidTokenError as e:
        raise credentials_exception

    user = await user_repo.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception

    return user
