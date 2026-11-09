from typing import Protocol

from src.domain.entities.payment import Payment


class PaymentRepository(Protocol):
    async def list_by_user_id(self, user_id: int) -> list[Payment]: ...

    async def add_if_absent(self, payment: Payment) -> bool:
        """Return False if a payment with the same external_id already exists."""
        ...
