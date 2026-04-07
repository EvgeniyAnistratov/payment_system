from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from payment_system.models import Account, User
from payment_system.models import Account


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

    async def get_users_with_accounts(self):
        user_cols = [
            self.model.id, self.model.first_name, self.model.surname,
            self.model.last_name, self.model.email
        ]
        account_cols = [Account.id, Account.balance]

        stmt = select(self.model) \
            .options(joinedload(self.model.accounts).load_only(*account_cols)) \
            .options(load_only(*user_cols)) \
            .order_by(self.model.id)
        users = await self.session.execute(stmt)
        return users.scalars().unique().all()
