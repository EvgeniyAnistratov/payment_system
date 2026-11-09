from dataclasses import dataclass

from src.domain.errors.base import DomainValidationError


@dataclass(frozen=True, slots=True)
class Money:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise DomainValidationError("Amount must be positive")
