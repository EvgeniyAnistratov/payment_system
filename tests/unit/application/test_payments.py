import pytest

from src.application.dtos.auth import AuthContext
from src.application.dtos.payment import ProcessPaymentInput
from src.application.errors.access_denied import AccessDeniedError
from src.application.errors.invalid_signature import InvalidSignatureError
from src.application.use_cases.accounts.list_user_accounts import ListUserAccountsUseCase
from src.application.use_cases.payments.list_user_payments import ListUserPaymentsUseCase
from src.application.use_cases.payments.process_payment import ProcessPaymentUseCase
from src.domain.entities.account import Account
from src.domain.entities.payment import Payment
from src.domain.errors.account import AccountOwnershipMismatchError
from src.domain.errors.base import DomainValidationError
from src.domain.errors.common import NotFoundError
from src.domain.value_objects.money import Money
from src.domain.value_objects.role import Role
from tests.helpers.factories import add_account, add_user, make_user
from tests.helpers.fakes.adapters import FakePaymentSignatureVerifier, FakeTransactionManager
from tests.helpers.fakes.repositories import (
    InMemoryAccountRepository,
    InMemoryPaymentRepository,
    InMemoryUserRepository,
)
from tests.helpers.fakes.store import InMemoryStore

ADMIN = AuthContext(user_id=1, role=Role.ADMIN)
USER = AuthContext(user_id=2, role=Role.USER)
OTHER = AuthContext(user_id=3, role=Role.USER)
SIGNATURE = "ab" * 16


def _payment(**overrides: object) -> ProcessPaymentInput:
    values: dict[str, object] = {
        "transaction_id": "tx-1",
        "account_id": 10,
        "user_id": 2,
        "amount": 15,
        "signature": SIGNATURE,
    }
    values.update(overrides)
    return ProcessPaymentInput(**values)  # type: ignore[arg-type]


def _use_case(
    store: InMemoryStore,
    *,
    valid: bool = True,
) -> tuple[ProcessPaymentUseCase, FakeTransactionManager]:
    transactions = FakeTransactionManager(store)
    use_case = ProcessPaymentUseCase(
        transactions,
        FakePaymentSignatureVerifier(valid),
        InMemoryUserRepository(store),
        InMemoryAccountRepository(store),
        InMemoryPaymentRepository(store),
    )
    return use_case, transactions


async def test_payment_opens_a_new_account_with_the_amount() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    use_case, transactions = _use_case(store)

    await use_case.execute(_payment())

    account = store.accounts[10]
    assert account.user_id == 2
    assert account.balance == 15
    assert store.payments["tx-1"].amount.value == 15
    assert transactions.commits == 1


async def test_payment_increases_an_existing_account() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    add_account(store, Account(id=10, user_id=2, balance=50))
    use_case, _transactions = _use_case(store)

    await use_case.execute(_payment(amount=20))

    assert store.accounts[10].balance == 70


async def test_duplicate_transaction_id_does_not_change_the_balance() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    use_case, transactions = _use_case(store)

    await use_case.execute(_payment())
    await use_case.execute(_payment(amount=40))

    assert store.accounts[10].balance == 15
    assert len(store.payments) == 1
    assert transactions.commits == 2


async def test_invalid_signature_stores_nothing_and_skips_the_transaction() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    use_case, transactions = _use_case(store, valid=False)

    with pytest.raises(InvalidSignatureError, match="Invalid signature"):
        await use_case.execute(_payment())

    assert store.accounts == {}
    assert store.payments == {}
    assert transactions.entered == 0


async def test_unknown_user_is_not_found_and_stores_nothing() -> None:
    store = InMemoryStore()
    use_case, transactions = _use_case(store)

    with pytest.raises(NotFoundError, match="User 2 not found"):
        await use_case.execute(_payment())

    assert store.accounts == {}
    assert store.payments == {}
    assert transactions.rollbacks == 1


async def test_foreign_account_is_rejected_and_rolled_back() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    add_user(store, make_user(user_id=3, email="other@example.com"))
    add_account(store, Account(id=10, user_id=3, balance=50))
    use_case, transactions = _use_case(store)

    with pytest.raises(AccountOwnershipMismatchError):
        await use_case.execute(_payment(user_id=2, account_id=10))

    assert store.accounts[10].balance == 50
    assert store.accounts[10].user_id == 3
    assert store.payments == {}
    assert transactions.rollbacks == 1


async def test_non_positive_amount_fails_before_the_transaction() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    use_case, transactions = _use_case(store)

    with pytest.raises(DomainValidationError, match="Amount must be positive"):
        await use_case.execute(_payment(amount=0))

    assert transactions.entered == 0


async def test_owner_lists_accounts_and_a_stranger_does_not() -> None:
    store = InMemoryStore()
    add_account(store, Account(id=1, user_id=2, balance=50))
    use_case = ListUserAccountsUseCase(InMemoryAccountRepository(store))

    accounts = await use_case.execute(USER, 2)
    assert [(account.id, account.balance) for account in accounts] == [(1, 50)]

    listed_by_admin = await use_case.execute(ADMIN, 2)
    assert listed_by_admin[0].user_id == 2

    with pytest.raises(AccessDeniedError):
        await use_case.execute(OTHER, 2)

    assert await use_case.execute(ADMIN, 9) == []


async def test_owner_lists_payments() -> None:
    store = InMemoryStore()
    store.payments["tx-1"] = Payment(
        external_id="tx-1",
        user_id=2,
        account_id=1,
        amount=Money(15),
        signature=bytes.fromhex(SIGNATURE),
        id=7,
    )
    use_case = ListUserPaymentsUseCase(InMemoryPaymentRepository(store))

    payments = await use_case.execute(USER, 2)

    assert payments[0].id == 7
    assert payments[0].transaction_id == "tx-1"
    assert payments[0].signature == SIGNATURE
    with pytest.raises(AccessDeniedError):
        await use_case.execute(OTHER, 2)
