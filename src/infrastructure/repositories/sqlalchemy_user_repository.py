from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors.repository import RepositoryError
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.infrastructure.db.guard import translate_errors
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.mappers.user_mapper import UserMapper


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: int) -> User | None:
        model = await translate_errors(self._session.get(UserModel, user_id))
        if model is None:
            return None
        return UserMapper.to_domain(model)

    async def find_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)
        model = await translate_errors(self._session.scalar(stmt))
        if model is None:
            return None
        return UserMapper.to_domain(model)

    async def add(self, user: User) -> User:
        model = UserModel(**UserMapper.to_persistence(user))
        self._session.add(model)
        await translate_errors(self._session.flush())
        return UserMapper.to_domain(model)

    async def save(self, user: User) -> None:
        if user.id is None:
            raise RepositoryError("User id is missing")
        model = await translate_errors(self._session.get(UserModel, user.id))
        if model is None:
            raise RepositoryError(f"User {user.id} not found")
        for field, value in UserMapper.to_persistence(user).items():
            setattr(model, field, value)
        await translate_errors(self._session.flush())

    async def delete(self, user_id: int) -> bool:
        stmt = delete(UserModel).where(UserModel.id == user_id)
        result = await translate_errors(self._session.execute(stmt))
        return result.rowcount > 0
