from src.domain.entities.payment import Payment
from src.domain.value_objects.money import Money
from src.infrastructure.db.models.payment import PaymentModel


class PaymentMapper:
    @staticmethod
    def to_domain(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            external_id=model.transaction_id,
            user_id=model.user_id,
            account_id=model.account_id,
            amount=Money(model.amount),
            signature=bytes(model.signature),
        )

    @staticmethod
    def to_persistence(entity: Payment) -> dict[str, object]:
        data: dict[str, object] = {
            "amount": entity.amount.value,
            "user_id": entity.user_id,
            "account_id": entity.account_id,
            "transaction_id": entity.external_id,
            "signature": entity.signature,
        }
        if entity.id is not None:
            data["id"] = entity.id
        return data
