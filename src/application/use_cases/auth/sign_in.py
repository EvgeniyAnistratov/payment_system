from src.application.dtos.auth import AccessTokenOutput, SignInInput
from src.application.ports.access_token_issuer import AccessTokenIssuer
from src.application.ports.password_hasher import PasswordHasher
from src.domain.errors.auth import InvalidCredentialsError
from src.domain.errors.base import DomainValidationError
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email

_INVALID_CREDENTIALS = "Could not validate credentials"


class SignInUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_issuer: AccessTokenIssuer,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_issuer = token_issuer

    async def execute(self, data: SignInInput) -> AccessTokenOutput:
        try:
            email = Email.create(data.email)
        except DomainValidationError:
            raise InvalidCredentialsError(_INVALID_CREDENTIALS) from None

        user = await self._user_repository.find_by_email(email)
        if user is None or user.id is None:
            raise InvalidCredentialsError(_INVALID_CREDENTIALS)
        if not await self._password_hasher.verify(data.password, user.password_hash):
            raise InvalidCredentialsError(_INVALID_CREDENTIALS)

        return AccessTokenOutput(access_token=self._token_issuer.issue(user.id))
