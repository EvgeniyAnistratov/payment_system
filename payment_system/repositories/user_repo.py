from sqlalchemy.ext.asyncio import AsyncSession

from payment_system.models import User


class UserRepo:
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int):
        return await self.session.get(self.model, id)
