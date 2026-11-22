from collections.abc import Awaitable
from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError

from src.application.errors.repository import RepositoryError

T = TypeVar("T")


async def translate_errors(awaitable: Awaitable[T]) -> T:
    try:
        return await awaitable
    except SQLAlchemyError as exc:
        raise RepositoryError("Database operation failed") from exc
