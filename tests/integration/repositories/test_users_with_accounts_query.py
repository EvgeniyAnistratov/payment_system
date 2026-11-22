from uuid import uuid4

from src.domain.entities.account import Account
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from src.infrastructure.repositories.sqlalchemy_account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.repositories.sqlalchemy_users_with_accounts_query import (
    SqlAlchemyUsersWithAccountsQuery,
)


async def test_fetch_returns_users_with_account_balances(db_session) -> None:
    email = Email.create(f"listed-{uuid4()}@example.com")
    user = await SqlAlchemyUserRepository(db_session).add(
        User(
            first_name="Ivan",
            surname="Ivanov",
            last_name="Ivanovich",
            email=email,
            password_hash="hash",
            role=Role.USER,
        )
    )
    assert user.id is not None
    await SqlAlchemyAccountRepository(db_session).add_if_absent(
        Account(id=920_201, user_id=user.id, balance=70)
    )

    rows = await SqlAlchemyUsersWithAccountsQuery(db_session).fetch()
    listed = next(row for row in rows if row.id == user.id)

    assert listed.email == email.value
    assert listed.full_name == "Ivanov Ivan Ivanovich"
    assert [(account.id, account.balance) for account in listed.accounts] == [(920_201, 70)]
