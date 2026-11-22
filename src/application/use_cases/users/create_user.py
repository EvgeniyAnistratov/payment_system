from src.application.dtos.auth import AuthContext
from src.application.dtos.user import CreateUserInput, UserOutput, to_user_output
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.transaction_manager import TransactionManager
from src.application.services.access_policy import ensure_admin
from src.domain.entities.user import User
from src.domain.errors.common import AlreadyExistsError
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email


class CreateUserUseCase:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction_manager = transaction_manager
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, actor: AuthContext, data: CreateUserInput) -> UserOutput:
        ensure_admin(actor)
        email = Email.create(data.email)
        async with self._transaction_manager.transaction():
            if await self._user_repository.find_by_email(email) is not None:
                raise AlreadyExistsError(f"A user with email {email.value} already exists")
            password_hash = await self._password_hasher.hash(data.password)
            user = User.create(
                data.first_name,
                data.surname,
                data.last_name,
                email,
                password_hash,
            )
            saved = await self._user_repository.add(user)
            return to_user_output(saved)
