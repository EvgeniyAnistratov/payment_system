from uuid import uuid4

from src.domain.entities.account import Account
from src.domain.entities.payment import Payment
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.domain.value_objects.role import Role
from src.infrastructure.repositories.sqlalchemy_account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.sqlalchemy_payment_repository import (
    SqlAlchemyPaymentRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


async def test_duplicate_external_id_is_not_inserted(db_session) -> None:
    user = await SqlAlchemyUserRepository(db_session).add(
        User(
            first_name="Petr",
            surname="Petrov",
            last_name=None,
            email=Email.create(f"payment-{uuid4()}@example.com"),
            password_hash="hash",
            role=Role.USER,
        )
    )
    assert user.id is not None
    account = Account.open(920_101, user.id)
    await SqlAlchemyAccountRepository(db_session).add_if_absent(account)
    repository = SqlAlchemyPaymentRepository(db_session)
    payment = Payment(
        external_id=f"tx-{uuid4()}",
        user_id=user.id,
        account_id=account.id,
        amount=Money(15),
        signature=b"\x01" * 32,
    )

    assert await repository.add_if_absent(payment) is True
    assert payment.id is not None
    assert await repository.add_if_absent(payment) is False

    stored = await repository.list_by_user_id(user.id)
    assert len(stored) == 1
    assert stored[0].external_id == payment.external_id
    assert stored[0].signature == b"\x01" * 32
