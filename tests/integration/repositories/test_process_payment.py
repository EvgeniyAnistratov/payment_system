import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import delete

from src.application.dtos.payment import ProcessPaymentInput
from src.application.use_cases.payments.process_payment import ProcessPaymentUseCase
from src.domain.entities.account import Account
from src.domain.entities.user import User
from src.domain.errors.account import AccountOwnershipMismatchError
from src.domain.errors.common import NotFoundError
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from src.infrastructure.config.settings import AppSettings
from src.infrastructure.db.engine import create_session_factory
from src.infrastructure.db.models.account import AccountModel
from src.infrastructure.db.models.payment import PaymentModel
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.repositories.sqlalchemy_account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.sqlalchemy_payment_repository import (
    SqlAlchemyPaymentRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.services.sha256_payment_signature import Sha256PaymentSignature
from src.infrastructure.services.sqlalchemy_transaction_manager import SqlAlchemyTransactionManager


def _use_case(session, signer: Sha256PaymentSignature) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(
        SqlAlchemyTransactionManager(session),
        signer,
        SqlAlchemyUserRepository(session),
        SqlAlchemyAccountRepository(session),
        SqlAlchemyPaymentRepository(session),
    )


def _payment(signer: Sha256PaymentSignature, **values: object) -> ProcessPaymentInput:
    draft = ProcessPaymentInput(signature="", **values)  # type: ignore[arg-type]
    return ProcessPaymentInput(signature=signer.sign(draft), **values)  # type: ignore[arg-type]


async def _add_user(session, email: str) -> int:
    user = await SqlAlchemyUserRepository(session).add(
        User(
            first_name="Petr",
            surname="Petrov",
            last_name=None,
            email=Email.create(email),
            password_hash="hash",
            role=Role.USER,
        )
    )
    assert user.id is not None
    return user.id


async def test_payment_opens_an_account_and_is_idempotent(db_session) -> None:
    signer = Sha256PaymentSignature(AppSettings())
    user_id = await _add_user(db_session, f"pay-{uuid4()}@example.com")
    use_case = _use_case(db_session, signer)
    payload = _payment(
        signer,
        transaction_id=f"tx-{uuid4()}",
        account_id=920_301,
        user_id=user_id,
        amount=15,
    )

    await use_case.execute(payload)
    await use_case.execute(payload)

    account = await SqlAlchemyAccountRepository(db_session).get_for_update(920_301)
    payments = await SqlAlchemyPaymentRepository(db_session).list_by_user_id(user_id)
    assert account is not None
    assert account.balance == 15
    assert len(payments) == 1


async def test_payment_increases_an_existing_account(db_session) -> None:
    signer = Sha256PaymentSignature(AppSettings())
    user_id = await _add_user(db_session, f"pay-existing-{uuid4()}@example.com")
    await SqlAlchemyAccountRepository(db_session).add_if_absent(
        Account(id=920_302, user_id=user_id, balance=50)
    )

    await _use_case(db_session, signer).execute(
        _payment(
            signer,
            transaction_id=f"tx-{uuid4()}",
            account_id=920_302,
            user_id=user_id,
            amount=20,
        )
    )

    account = await SqlAlchemyAccountRepository(db_session).get_for_update(920_302)
    assert account is not None
    assert account.balance == 70


async def test_unknown_user_stores_nothing(db_session) -> None:
    signer = Sha256PaymentSignature(AppSettings())

    with pytest.raises(NotFoundError):
        await _use_case(db_session, signer).execute(
            _payment(
                signer,
                transaction_id=f"tx-{uuid4()}",
                account_id=920_303,
                user_id=999_999,
                amount=10,
            )
        )

    assert await SqlAlchemyAccountRepository(db_session).get_for_update(920_303) is None


async def test_foreign_account_is_rolled_back(db_session) -> None:
    signer = Sha256PaymentSignature(AppSettings())
    accounts = SqlAlchemyAccountRepository(db_session)
    async with SqlAlchemyTransactionManager(db_session).transaction():
        owner_id = await _add_user(db_session, f"owner-{uuid4()}@example.com")
        payer_id = await _add_user(db_session, f"payer-{uuid4()}@example.com")
        await accounts.add_if_absent(Account(id=920_304, user_id=owner_id, balance=50))

    with pytest.raises(AccountOwnershipMismatchError):
        await _use_case(db_session, signer).execute(
            _payment(
                signer,
                transaction_id=f"tx-{uuid4()}",
                account_id=920_304,
                user_id=payer_id,
                amount=10,
            )
        )

    account = await SqlAlchemyAccountRepository(db_session).get_for_update(920_304)
    payments = await SqlAlchemyPaymentRepository(db_session).list_by_user_id(payer_id)
    assert account is not None
    assert account.balance == 50
    assert payments == []


async def test_parallel_payments_on_a_new_account_sum_the_balance(engine) -> None:
    signer = Sha256PaymentSignature(AppSettings())
    factory = create_session_factory(engine)
    account_id = 920_305
    amounts = [1, 2, 3, 4, 5, 6, 7, 8]
    user_id: int | None = None

    async def cleanup() -> None:
        async with factory() as session:
            async with SqlAlchemyTransactionManager(session).transaction():
                await session.execute(
                    delete(PaymentModel).where(PaymentModel.account_id == account_id)
                )
                await session.execute(delete(AccountModel).where(AccountModel.id == account_id))
                if user_id is not None:
                    await session.execute(delete(UserModel).where(UserModel.id == user_id))

    await cleanup()
    try:
        async with factory() as session:
            async with SqlAlchemyTransactionManager(session).transaction():
                user_id = await _add_user(session, f"parallel-{uuid4()}@example.com")

        async def pay(amount: int, number: int) -> None:
            async with factory() as session:
                await _use_case(session, signer).execute(
                    _payment(
                        signer,
                        transaction_id=f"parallel-{user_id}-{number}",
                        account_id=account_id,
                        user_id=user_id,
                        amount=amount,
                    )
                )

        await asyncio.gather(*(pay(amount, number) for number, amount in enumerate(amounts)))

        async with factory() as session:
            account = await SqlAlchemyAccountRepository(session).get_for_update(account_id)
            payments = await SqlAlchemyPaymentRepository(session).list_by_user_id(user_id)
        assert account is not None
        assert account.balance == sum(amounts)
        assert len(payments) == len(amounts)
    finally:
        await cleanup()
