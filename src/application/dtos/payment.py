from dataclasses import dataclass

from src.application.errors.repository import RepositoryError
from src.domain.entities.payment import Payment


@dataclass(frozen=True, slots=True)
class ProcessPaymentInput:
    transaction_id: str
    account_id: int
    user_id: int
    amount: int
    signature: str


@dataclass(frozen=True, slots=True)
class PaymentOutput:
    id: int
    amount: int
    user_id: int
    account_id: int
    transaction_id: str
    signature: str


def to_payment_output(payment: Payment) -> PaymentOutput:
    if payment.id is None:
        raise RepositoryError("Payment id is missing")
    return PaymentOutput(
        id=payment.id,
        amount=payment.amount.value,
        user_id=payment.user_id,
        account_id=payment.account_id,
        transaction_id=payment.external_id,
        signature=payment.signature.hex(),
    )
