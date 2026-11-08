from uuid import uuid4


def payment_payload(
    *,
    user_id: int,
    account_id: int,
    amount: int,
    transaction_id: str | None = None,
    signature: str | None = None,
) -> dict:
    payload = {
        "user_id": user_id,
        "account_id": account_id,
        "amount": amount,
        "transaction_id": transaction_id or str(uuid4()),
    }
    if signature is None:
        from app.core.settings import APP_TRANSACTION_SECRET
        from app.utils.signature import generate_signature

        signature = generate_signature(payload, APP_TRANSACTION_SECRET)
    payload["signature"] = signature
    return payload
