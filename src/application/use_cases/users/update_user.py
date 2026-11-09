from src.application.dtos.auth import AuthContext
from src.application.dtos.user import UNSET, UpdateUserInput, UserOutput, to_user_output
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.transaction_manager import TransactionManager
from src.application.services.access_policy import ensure_admin
from src.domain.errors.common import AlreadyExistsError, NotFoundError
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email


class UpdateUserUseCase:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction_manager = transaction_manager
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(
        self,
        actor: AuthContext,
        user_id: int,
        data: UpdateUserInput,
    ) -> UserOutput:
        ensure_admin(actor)
        async with self._transaction_manager.transaction():
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                raise NotFoundError(f"User {user_id} not found")

            if data.email is not None:
                email = Email.create(data.email)
                existing = await self._user_repository.find_by_email(email)
                if existing is not None and existing.id != user.id:
                    raise AlreadyExistsError(f"A user with email {email.value} already exists")
                user.change_email(email)

            if data.password is not None:
                user.change_password(await self._password_hasher.hash(data.password))

            rename_args: dict[str, str | None] = {}
            if data.first_name is not None:
                rename_args["first_name"] = data.first_name
            if data.surname is not None:
                rename_args["surname"] = data.surname
            if data.last_name is not UNSET:
                rename_args["last_name"] = data.last_name
            if rename_args:
                user.rename(**rename_args)

            await self._user_repository.save(user)
            return to_user_output(user)
