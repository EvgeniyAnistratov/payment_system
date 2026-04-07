from payment_system.repositories import TransactionRepo
from payment_system.schemes import TransactionScheme


class TransactionService:
    def __init__(self, repo: TransactionRepo):
        self.repo: TransactionRepo = repo

    async def get_list_by_user_id(self, user_id: int):
        accounts = await self.repo.get_by_user_id(user_id)
        return [TransactionScheme.model_validate(obj, from_attributes=True) for obj in accounts]
