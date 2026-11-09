from src.application.dtos.auth import AuthContext
from src.application.dtos.user import UserOutput, to_user_output
from src.application.services.access_policy import ensure_owner_or_admin
from src.domain.errors.common import NotFoundError
from src.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, actor: AuthContext, user_id: int) -> UserOutput:
        ensure_owner_or_admin(actor, user_id)
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return to_user_output(user)
