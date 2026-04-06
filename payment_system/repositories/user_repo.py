from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from payment_system.models import User


class UserRepo:
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int):
        return await self.session.get(self.model, user_id)

    async def get_by_email(self, email: str):
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
