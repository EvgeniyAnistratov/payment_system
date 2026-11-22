from uuid import uuid4

import pytest

from src.application.errors.repository import RepositoryError
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.sqlalchemy_transaction_manager import SqlAlchemyTransactionManager


def _user(email: str, *, role: Role = Role.USER) -> User:
    return User(
        first_name="Petr",
        surname="Petrov",
        last_name=None,
        email=Email.create(email),
        password_hash="hash",
        role=role,
    )


async def test_add_find_and_save_a_user(db_session) -> None:
    repository = SqlAlchemyUserRepository(db_session)
    email = Email.create(f"petr-{uuid4()}@example.com")

    created = await repository.add(_user(email.value))
    found = await repository.find_by_id(created.id)
    by_email = await repository.find_by_email(email)

    assert found is not None
    assert found.id == created.id
    assert by_email is not None
    assert by_email.email == email
    assert found.role is Role.USER
    assert found.full_name == "Petrov Petr"

    found.change_email(Email.create(f"new-{uuid4()}@example.com"))
    await repository.save(found)
    updated = await repository.find_by_id(found.id)
    assert updated is not None
    assert updated.email == found.email


async def test_duplicate_email_is_a_repository_error(db_session) -> None:
    repository = SqlAlchemyUserRepository(db_session)
    email = f"taken-{uuid4()}@example.com"
    await repository.add(_user(email))

    with pytest.raises(RepositoryError):
        await repository.add(_user(email))


async def test_delete_commits_and_a_missing_user_returns_false(db_session) -> None:
    repository = SqlAlchemyUserRepository(db_session)
    manager = SqlAlchemyTransactionManager(db_session)
    created = await repository.add(_user(f"delete-{uuid4()}@example.com"))

    async with manager.transaction():
        assert await repository.delete(created.id) is True

    assert await repository.find_by_id(created.id) is None
    async with manager.transaction():
        assert await repository.delete(created.id) is False


async def test_seed_user_is_readable(db_session) -> None:
    user = await SqlAlchemyUserRepository(db_session).find_by_email(
        Email.create("ivan@example.com")
    )

    assert user is not None
    assert user.id == 2
    assert user.full_name == "Ivanov Ivan Ivanovich"
    assert user.role is Role.USER
    assert await BcryptPasswordHasher().verify("user_password", user.password_hash)
