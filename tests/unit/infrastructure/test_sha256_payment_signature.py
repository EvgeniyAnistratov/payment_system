from pydantic import SecretStr

from src.application.dtos.payment import ProcessPaymentInput
from src.infrastructure.config.settings import AppSettings
from src.infrastructure.services.sha256_payment_signature import Sha256PaymentSignature

_EXAMPLE = ProcessPaymentInput(
    transaction_id="5eae174f-7cd0-472c-bd36-35660f00132b",
    user_id=1,
    account_id=1,
    amount=100,
    signature="7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
)


def _signer(secret: str) -> Sha256PaymentSignature:
    return Sha256PaymentSignature(AppSettings(transaction_secret=SecretStr(secret)))


def test_assignment_example_signature_matches() -> None:
    signer = _signer("gfdmhghif38yrf9ew0jkf32")

    assert signer.sign(_EXAMPLE) == _EXAMPLE.signature
    assert signer.verify(_EXAMPLE) is True


def test_verify_rejects_a_different_signature() -> None:
    signer = _signer("gfdmhghif38yrf9ew0jkf32")
    forged = ProcessPaymentInput(
        transaction_id=_EXAMPLE.transaction_id,
        user_id=_EXAMPLE.user_id,
        account_id=_EXAMPLE.account_id,
        amount=_EXAMPLE.amount,
        signature="00" * 32,
    )

    assert signer.verify(forged) is False
