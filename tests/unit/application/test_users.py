import pytest

from src.application.dtos.auth import AuthContext
from src.application.dtos.user import (
    UNSET,
    CreateUserInput,
    UpdateUserInput,
    UserWithAccountsOutput,
)
from src.application.errors.access_denied import AccessDeniedError
from src.application.use_cases.users.create_user import CreateUserUseCase
from src.application.use_cases.users.delete_user import DeleteUserUseCase
from src.application.use_cases.users.get_user import GetUserUseCase
from src.application.use_cases.users.list_users_with_accounts import ListUsersWithAccountsUseCase
from src.application.use_cases.users.update_user import UpdateUserUseCase
from src.domain.errors.common import AlreadyExistsError, NotFoundError
from src.domain.value_objects.role import Role
from tests.helpers.factories import add_user, make_user
from tests.helpers.fakes.adapters import (
    FakePasswordHasher,
    FakeTransactionManager,
    InMemoryUsersWithAccountsQuery,
)
from tests.helpers.fakes.repositories import InMemoryUserRepository
from tests.helpers.fakes.store import InMemoryStore

ADMIN = AuthContext(user_id=1, role=Role.ADMIN)
USER = AuthContext(user_id=2, role=Role.USER)


def _users(store: InMemoryStore) -> tuple[InMemoryUserRepository, FakeTransactionManager]:
    return InMemoryUserRepository(store), FakeTransactionManager(store)


async def test_admin_creates_a_user_inside_a_transaction() -> None:
    store = InMemoryStore()
    users, transactions = _users(store)
    use_case = CreateUserUseCase(transactions, users, FakePasswordHasher())

    created = await use_case.execute(
        ADMIN,
        CreateUserInput(
            first_name="Petr",
            surname="Petrov",
            last_name=None,
            email=" Petr@Example.com ",
            password="secret",
        ),
    )

    assert created.id == 1
    assert created.email == "petr@example.com"
    assert created.full_name == "Petrov Petr"
    saved = await users.find_by_id(created.id)
    assert saved is not None
    assert saved.password_hash == "hashed:secret"
    assert saved.role is Role.USER
    assert transactions.commits == 1


async def test_create_user_rejects_a_taken_email_and_rolls_back() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2, email="ivan@example.com"))
    users, transactions = _users(store)
    use_case = CreateUserUseCase(transactions, users, FakePasswordHasher())

    with pytest.raises(
        AlreadyExistsError,
        match="A user with email ivan@example.com already exists",
    ):
        await use_case.execute(
            ADMIN,
            CreateUserInput("Petr", "Petrov", None, "Ivan@Example.com", "secret"),
        )

    assert await users.find_by_email(store.users[2].email) is store.users[2]
    assert len(store.users) == 1
    assert transactions.rollbacks == 1
    assert transactions.commits == 0


async def test_user_cannot_create_another_user() -> None:
    store = InMemoryStore()
    users, transactions = _users(store)

    with pytest.raises(AccessDeniedError):
        await CreateUserUseCase(transactions, users, FakePasswordHasher()).execute(
            USER,
            CreateUserInput("Petr", "Petrov", None, "petr@example.com", "secret"),
        )

    assert transactions.entered == 0
    assert store.users == {}


async def test_owner_reads_himself_and_a_stranger_is_forbidden() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    use_case = GetUserUseCase(InMemoryUserRepository(store))

    found = await use_case.execute(USER, 2)
    assert found.full_name == "Ivanov Ivan Ivanovich"

    with pytest.raises(AccessDeniedError):
        await use_case.execute(AuthContext(user_id=3, role=Role.USER), 2)


async def test_admin_gets_not_found_for_a_missing_user() -> None:
    use_case = GetUserUseCase(InMemoryUserRepository(InMemoryStore()))

    with pytest.raises(NotFoundError, match="User 9 not found"):
        await use_case.execute(ADMIN, 9)


async def test_update_clears_last_name_and_keeps_an_omitted_one() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    users, transactions = _users(store)
    use_case = UpdateUserUseCase(transactions, users, FakePasswordHasher())

    cleared = await use_case.execute(ADMIN, 2, UpdateUserInput(last_name=None))
    assert cleared.full_name == "Ivanov Ivan"

    kept = await use_case.execute(ADMIN, 2, UpdateUserInput(first_name="Pyotr"))
    assert kept.full_name == "Ivanov Pyotr"
    assert kept.email == "ivan@example.com"
    saved = await users.find_by_id(2)
    assert saved is not None
    assert saved.password_hash == "hashed:user_password"
    assert UpdateUserInput().last_name is UNSET


async def test_update_changes_email_and_password() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    users, transactions = _users(store)

    updated = await UpdateUserUseCase(transactions, users, FakePasswordHasher()).execute(
        ADMIN,
        2,
        UpdateUserInput(email="New@Example.com", password="new-secret"),
    )

    saved = await users.find_by_id(2)
    assert updated.email == "new@example.com"
    assert saved is not None
    assert saved.password_hash == "hashed:new-secret"
    assert transactions.commits == 1


async def test_update_rejects_an_email_taken_by_someone_else() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2, email="ivan@example.com"))
    add_user(
        store,
        make_user(user_id=3, email="petr@example.com", first_name="Petr", surname="Petrov"),
    )
    users, transactions = _users(store)

    with pytest.raises(
        AlreadyExistsError,
        match="A user with email petr@example.com already exists",
    ):
        await UpdateUserUseCase(transactions, users, FakePasswordHasher()).execute(
            ADMIN,
            2,
            UpdateUserInput(email="petr@example.com"),
        )

    assert store.users[2].email.value == "ivan@example.com"
    assert transactions.rollbacks == 1


async def test_update_allows_keeping_the_same_email() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    users, transactions = _users(store)

    updated = await UpdateUserUseCase(transactions, users, FakePasswordHasher()).execute(
        ADMIN,
        2,
        UpdateUserInput(email="ivan@example.com", surname="Sidorov"),
    )

    assert updated.email == "ivan@example.com"
    assert updated.full_name == "Sidorov Ivan Ivanovich"


async def test_admin_deletes_a_user_and_commits() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    users, transactions = _users(store)

    await DeleteUserUseCase(transactions, users).execute(ADMIN, 2)

    assert await users.find_by_id(2) is None
    assert transactions.commits == 1


async def test_delete_of_a_missing_user_is_not_found() -> None:
    store = InMemoryStore()
    users, transactions = _users(store)

    with pytest.raises(NotFoundError, match="User 9 not found"):
        await DeleteUserUseCase(transactions, users).execute(ADMIN, 9)

    assert transactions.rollbacks == 1


async def test_user_cannot_delete_anyone() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))
    users, transactions = _users(store)

    with pytest.raises(AccessDeniedError):
        await DeleteUserUseCase(transactions, users).execute(USER, 2)

    assert transactions.entered == 0
    assert 2 in store.users


async def test_only_admin_lists_users_with_accounts() -> None:
    row = UserWithAccountsOutput(
        id=2,
        email="ivan@example.com",
        full_name="Ivanov Ivan",
        accounts=(),
    )
    use_case = ListUsersWithAccountsUseCase(InMemoryUsersWithAccountsQuery([row]))

    assert await use_case.execute(ADMIN) == [row]
    with pytest.raises(AccessDeniedError):
        await use_case.execute(USER)
