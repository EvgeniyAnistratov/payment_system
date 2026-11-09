from dataclasses import dataclass

from src.domain.errors.base import DomainValidationError
from src.domain.value_objects.money import Money


@dataclass(slots=True)
class Payment:
    external_id: str
    user_id: int
    account_id: int
    amount: Money
    signature: bytes
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.external_id:
            raise DomainValidationError("Transaction id must not be empty")
        if self.user_id <= 0:
            raise DomainValidationError("User id must be positive")
        if self.account_id <= 0:
            raise DomainValidationError("Account id must be positive")
        if self.id is not None and self.id <= 0:
            raise DomainValidationError("Payment id must be positive")
