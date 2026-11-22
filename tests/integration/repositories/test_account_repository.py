from uuid import uuid4

from src.domain.entities.account import Account
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from src.infrastructure.repositories.sqlalchemy_account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


async def _owner(db_session) -> int:
    user = await SqlAlchemyUserRepository(db_session).add(
        User(
            first_name="Petr",
            surname="Petrov",
            last_name=None,
            email=Email.create(f"account-{uuid4()}@example.com"),
            password_hash="hash",
            role=Role.USER,
        )
    )
    assert user.id is not None
    return user.id


async def test_add_if_absent_does_not_overwrite_an_existing_account(db_session) -> None:
    user_id = await _owner(db_session)
    other_id = await _owner(db_session)
    repository = SqlAlchemyAccountRepository(db_session)
    account_id = 920_001

    await repository.add_if_absent(Account(id=account_id, user_id=user_id, balance=40))
    await repository.add_if_absent(Account.open(account_id, other_id))

    stored = await repository.get_for_update(account_id)
    assert stored is not None
    assert stored.user_id == user_id
    assert stored.balance == 40

    stored.balance = 55
    await repository.save(stored)
    updated = await repository.get_for_update(account_id)
    assert updated is not None
    assert updated.balance == 55
    assert [account.id for account in await repository.list_by_user_id(user_id)] == [account_id]
