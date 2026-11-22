import hashlib
import hmac

from src.application.dtos.payment import ProcessPaymentInput
from src.infrastructure.config.settings import AppSettings


class Sha256PaymentSignature:
    def __init__(self, settings: AppSettings) -> None:
        self._secret = settings.transaction_secret.get_secret_value()

    def sign(self, payment: ProcessPaymentInput) -> str:
        raw = _signed_payload(payment, self._secret)
        return hashlib.sha256(raw.encode()).hexdigest()

    def verify(self, payment: ProcessPaymentInput) -> bool:
        expected = self.sign(payment)
        try:
            return hmac.compare_digest(expected, payment.signature)
        except (TypeError, ValueError):
            return False


def _signed_payload(payment: ProcessPaymentInput, secret: str) -> str:
    payload = {
        "account_id": payment.account_id,
        "amount": payment.amount,
        "transaction_id": payment.transaction_id,
        "user_id": payment.user_id,
    }
    parts = [str(payload[key]) for key in sorted(payload)]
    parts.append(secret)
    return "".join(parts)
