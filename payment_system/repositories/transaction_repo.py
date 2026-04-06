from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_system.models import Transaction


class TransactionRepo:
    model = Transaction

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int):
        return await self.session.get(self.model, id)

    async def get_by_user_id(self, user_id: int):
        stmt = select(self.model).where(self.model.user_id == user_id)
        return await self.session.scalars(stmt)
