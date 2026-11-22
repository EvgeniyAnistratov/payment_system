from src.application.dtos.auth import AuthContext
from src.application.ports.transaction_manager import TransactionManager
from src.application.services.access_policy import ensure_admin
from src.domain.errors.common import NotFoundError
from src.domain.repositories.user_repository import UserRepository


class DeleteUserUseCase:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        user_repository: UserRepository,
    ) -> None:
        self._transaction_manager = transaction_manager
        self._user_repository = user_repository

    async def execute(self, actor: AuthContext, user_id: int) -> None:
        ensure_admin(actor)
        async with self._transaction_manager.transaction():
            if not await self._user_repository.delete(user_id):
                raise NotFoundError(f"User {user_id} not found")
