from src.domain.entities.account import Account
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from tests.helpers.fakes.store import InMemoryStore


def make_user(
    *,
    user_id: int,
    email: str = "ivan@example.com",
    role: Role = Role.USER,
    first_name: str = "Ivan",
    surname: str = "Ivanov",
    last_name: str | None = "Ivanovich",
    password_hash: str = "hashed:user_password",
) -> User:
    return User(
        first_name=first_name,
        surname=surname,
        last_name=last_name,
        email=Email.create(email),
        password_hash=password_hash,
        role=role,
        id=user_id,
    )


def add_user(store: InMemoryStore, user: User) -> User:
    if user.id is None:
        raise ValueError("User id is required")
    store.users[user.id] = user
    store.next_user_id = max(store.next_user_id, user.id + 1)
    return user


def add_account(store: InMemoryStore, account: Account) -> Account:
    store.accounts[account.id] = account
    return account
