from payment_system.repositories import AccountRepo
from payment_system.schemas import AccountSchema


class AccountService:
    def __init__(self, repo: AccountRepo):
        self.repo: AccountRepo = repo

    async def get_list_by_user_id(self, user_id: int):
        accounts = await self.repo.get_by_user_id(user_id)
        return [AccountSchema.model_validate(obj, from_attributes=True) for obj in accounts]
