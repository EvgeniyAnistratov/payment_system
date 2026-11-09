from src.application.dtos.auth import AuthContext
from src.application.dtos.payment import PaymentOutput, to_payment_output
from src.application.services.access_policy import ensure_owner_or_admin
from src.domain.repositories.payment_repository import PaymentRepository


class ListUserPaymentsUseCase:
    def __init__(self, payment_repository: PaymentRepository) -> None:
        self._payment_repository = payment_repository

    async def execute(self, actor: AuthContext, user_id: int) -> list[PaymentOutput]:
        ensure_owner_or_admin(actor, user_id)
        payments = await self._payment_repository.list_by_user_id(user_id)
        return [to_payment_output(payment) for payment in payments]
