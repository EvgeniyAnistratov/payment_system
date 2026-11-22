from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.application.dtos.auth import AuthContext
from src.application.ports.auth_context_resolver import AuthContextResolver
from src.presentation.errors.unauthorized import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


@inject
async def get_auth_context(
    token: Annotated[str, Depends(oauth2_scheme)],
    resolver: FromDishka[AuthContextResolver],
) -> AuthContext:
    auth = await resolver.resolve(token)
    if auth is None:
        raise UnauthorizedError("Could not validate credentials")
    return auth


CurrentActor = Annotated[AuthContext, Depends(get_auth_context)]
