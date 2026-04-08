from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction


class TransactionRepo:
    model = Transaction

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def create(self, transaction: Transaction):
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_by_id(self, id: int):
        return await self.session.get(self.model, id)

    async def get_by_user_id(self, user_id: int):
        stmt = select(self.model).where(self.model.user_id == user_id)
        return await self.session.scalars(stmt)

    async def get_by_transaction_id(self, transaction_id: str):
        stmt = select(self.model) \
            .where(self.model.transaction_id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
