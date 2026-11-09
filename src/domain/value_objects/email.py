import re
from dataclasses import dataclass

from src.domain.errors.base import DomainValidationError

_EMAIL_RE = re.compile(r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_RE.fullmatch(self.value):
            raise DomainValidationError(f"Invalid email format: {self.value}")

    @classmethod
    def create(cls, raw: str) -> "Email":
        normalized = raw.strip().lower()
        if not _EMAIL_RE.fullmatch(normalized):
            raise DomainValidationError(f"Invalid email format: {raw}")
        return cls(normalized)
