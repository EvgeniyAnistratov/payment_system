from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account


class AccountRepo:
    model = Account

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def create(self, account: Account):
        self.session.add(account)
        await self.session.flush()
        return account

    async def get_by_id(self, id: int):
        return await self.session.get(self.model, id)

    async def get_by_user_id(self, user_id: int):
        stmt = select(self.model).where(self.model.user_id == user_id)
        return await self.session.scalars(stmt)

    async def select_for_update(self, account_id: int):
        stmt = select(self.model).where(self.model.id == account_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
