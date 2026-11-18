from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.errors.repository import RepositoryError
from src.domain.entities.account import Account
from src.infrastructure.db.guard import translate_errors
from src.infrastructure.db.models.account import AccountModel
from src.infrastructure.mappers.account_mapper import AccountMapper


class SqlAlchemyAccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_user_id(self, user_id: int) -> list[Account]:
        stmt = (
            select(AccountModel).where(AccountModel.user_id == user_id).order_by(AccountModel.id)
        )
        models = await translate_errors(self._session.scalars(stmt))
        return [AccountMapper.to_domain(model) for model in models.all()]

    async def add_if_absent(self, account: Account) -> None:
        stmt = (
            insert(AccountModel)
            .values(**AccountMapper.to_persistence(account))
            .on_conflict_do_nothing(index_elements=[AccountModel.id])
        )
        await translate_errors(self._session.execute(stmt))

    async def get_for_update(self, account_id: int) -> Account | None:
        stmt = select(AccountModel).where(AccountModel.id == account_id).with_for_update()
        model = await translate_errors(self._session.scalar(stmt))
        if model is None:
            return None
        return AccountMapper.to_domain(model)

    async def save(self, account: Account) -> None:
        model = await translate_errors(self._session.get(AccountModel, account.id))
        if model is None:
            raise RepositoryError(f"Account {account.id} not found")
        model.user_id = account.user_id
        model.balance = account.balance
        await translate_errors(self._session.flush())
