from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_system.models import User


class UserRepo:
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def get_by_id(self, user_id: int):
        return await self.session.get(self.model, user_id)

    async def get_by_email(self, email: str):
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def delete_by_id(self, user_id: int):
        stmt = delete(self.model).where(self.model.id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount
