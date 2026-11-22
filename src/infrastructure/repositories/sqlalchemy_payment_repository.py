from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.payment import Payment
from src.infrastructure.db.guard import translate_errors
from src.infrastructure.db.models.payment import PaymentModel
from src.infrastructure.mappers.payment_mapper import PaymentMapper


class SqlAlchemyPaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_user_id(self, user_id: int) -> list[Payment]:
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.user_id == user_id)
            .order_by(PaymentModel.id)
        )
        models = await translate_errors(self._session.scalars(stmt))
        return [PaymentMapper.to_domain(model) for model in models.all()]

    async def add_if_absent(self, payment: Payment) -> bool:
        stmt = (
            insert(PaymentModel)
            .values(**PaymentMapper.to_persistence(payment))
            .on_conflict_do_nothing(index_elements=[PaymentModel.transaction_id])
            .returning(PaymentModel.id)
        )
        inserted_id = await translate_errors(self._session.scalar(stmt))
        if inserted_id is None:
            return False
        payment.id = inserted_id
        return True
