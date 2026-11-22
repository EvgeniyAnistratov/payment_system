from dataclasses import dataclass

from src.application.errors.repository import RepositoryError
from src.domain.entities.user import User


class Unset:
    """Marks a field that the caller did not send."""


UNSET = Unset()


@dataclass(frozen=True, slots=True)
class UserOutput:
    id: int
    email: str
    full_name: str


@dataclass(frozen=True, slots=True)
class AccountBalanceOutput:
    id: int
    balance: int


@dataclass(frozen=True, slots=True)
class UserWithAccountsOutput:
    id: int
    email: str
    full_name: str
    accounts: tuple[AccountBalanceOutput, ...]


@dataclass(frozen=True, slots=True)
class CreateUserInput:
    first_name: str
    surname: str
    last_name: str | None
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class UpdateUserInput:
    first_name: str | None = None
    surname: str | None = None
    last_name: str | None | Unset = UNSET
    email: str | None = None
    password: str | None = None


def to_user_output(user: User) -> UserOutput:
    if user.id is None:
        raise RepositoryError("User id is missing")
    return UserOutput(id=user.id, email=user.email.value, full_name=user.full_name)
