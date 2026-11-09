from src.application.dtos.account import AccountOutput, to_account_output
from src.application.dtos.auth import AuthContext
from src.application.services.access_policy import ensure_owner_or_admin
from src.domain.repositories.account_repository import AccountRepository


class ListUserAccountsUseCase:
    def __init__(self, account_repository: AccountRepository) -> None:
        self._account_repository = account_repository

    async def execute(self, actor: AuthContext, user_id: int) -> list[AccountOutput]:
        ensure_owner_or_admin(actor, user_id)
        accounts = await self._account_repository.list_by_user_id(user_id)
        return [to_account_output(account) for account in accounts]
