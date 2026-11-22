from uuid import uuid4

from src.application.dtos.payment import ProcessPaymentInput
from src.infrastructure.config.settings import AppSettings
from src.infrastructure.services.sha256_payment_signature import Sha256PaymentSignature


def payment_payload(
    *,
    user_id: int,
    account_id: int,
    amount: int,
    transaction_id: str | None = None,
    signature: str | None = None,
) -> dict:
    transaction_id = transaction_id or str(uuid4())
    if signature is None:
        draft = ProcessPaymentInput(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
            signature="",
        )
        signature = Sha256PaymentSignature(AppSettings()).sign(draft)
    return {
        "user_id": user_id,
        "account_id": account_id,
        "amount": amount,
        "transaction_id": transaction_id,
        "signature": signature,
    }
