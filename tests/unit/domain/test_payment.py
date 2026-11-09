import pytest

from src.domain.entities.payment import Payment
from src.domain.errors.base import DomainValidationError
from src.domain.value_objects.money import Money


def test_payment_keeps_the_idempotency_key() -> None:
    payment = Payment(
        external_id="5eae174f-7cd0-472c-bd36-35660f00132b",
        user_id=2,
        account_id=1,
        amount=Money(100),
        signature=b"\x00" * 32,
    )

    assert payment.id is None
    assert payment.external_id == "5eae174f-7cd0-472c-bd36-35660f00132b"
    assert payment.amount.value == 100


def test_payment_rejects_an_empty_transaction_id() -> None:
    with pytest.raises(DomainValidationError, match="Transaction id must not be empty"):
        Payment(
            external_id="",
            user_id=2,
            account_id=1,
            amount=Money(100),
            signature=b"\x00" * 32,
        )
