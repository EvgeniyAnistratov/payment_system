from src.application.dtos.auth import AuthContext
from src.application.dtos.user import UserWithAccountsOutput
from src.application.ports.queries.users_with_accounts_query import UsersWithAccountsQuery
from src.application.services.access_policy import ensure_admin


class ListUsersWithAccountsUseCase:
    def __init__(self, users_with_accounts_query: UsersWithAccountsQuery) -> None:
        self._users_with_accounts_query = users_with_accounts_query

    async def execute(self, actor: AuthContext) -> list[UserWithAccountsOutput]:
        ensure_admin(actor)
        return await self._users_with_accounts_query.fetch()
