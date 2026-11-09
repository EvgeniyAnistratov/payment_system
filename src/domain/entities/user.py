from dataclasses import dataclass

from src.domain.errors.base import DomainValidationError
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role

_UNSET = object()


def _require_name(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainValidationError(f"{field_name} must not be empty")
    return normalized


@dataclass(slots=True)
class User:
    first_name: str
    surname: str
    last_name: str | None
    email: Email
    password_hash: str
    role: Role
    id: int | None = None

    def __post_init__(self) -> None:
        self.first_name = _require_name(self.first_name, "First name")
        self.surname = _require_name(self.surname, "Surname")
        if self.last_name is not None:
            self.last_name = _require_name(self.last_name, "Last name")
        if not self.password_hash:
            raise DomainValidationError("Password hash must not be empty")
        if self.id is not None and self.id <= 0:
            raise DomainValidationError("User id must be positive")

    @classmethod
    def create(
        cls,
        first_name: str,
        surname: str,
        last_name: str | None,
        email: Email,
        password_hash: str,
    ) -> "User":
        return cls(first_name, surname, last_name, email, password_hash, Role.USER)

    @property
    def full_name(self) -> str:
        parts = [self.surname, self.first_name, self.last_name]
        return " ".join(part for part in parts if part)

    def change_email(self, email: Email) -> None:
        self.email = email

    def change_password(self, password_hash: str) -> None:
        if not password_hash:
            raise DomainValidationError("Password hash must not be empty")
        self.password_hash = password_hash

    def rename(
        self,
        *,
        first_name: str | None = None,
        surname: str | None = None,
        last_name: str | None | object = _UNSET,
    ) -> None:
        """Update name parts. Omitted fields stay as they are.

        ``last_name=None`` clears the patronymic. Leaving the argument out does not.
        """
        if first_name is not None:
            self.first_name = _require_name(first_name, "First name")
        if surname is not None:
            self.surname = _require_name(surname, "Surname")
        if last_name is not _UNSET:
            if last_name is None:
                self.last_name = None
            elif isinstance(last_name, str):
                self.last_name = _require_name(last_name, "Last name")
            else:
                raise DomainValidationError("Last name must be a string")
