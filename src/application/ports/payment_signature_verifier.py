from typing import Protocol

from src.application.dtos.payment import ProcessPaymentInput


class PaymentSignatureVerifier(Protocol):
    def verify(self, payment: ProcessPaymentInput) -> bool: ...
