import pytest

from src.domain.entities.user import User
from src.domain.errors.base import DomainValidationError
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role


def _user(**overrides: object) -> User:
    values: dict[str, object] = {
        "first_name": "Ivan",
        "surname": "Ivanov",
        "last_name": "Ivanovich",
        "email": Email.create("ivan@example.com"),
        "password_hash": "hash",
        "role": Role.USER,
    }
    values.update(overrides)
    return User(**values)  # type: ignore[arg-type]


def test_create_builds_a_user_without_id() -> None:
    user = User.create(
        "Ivan",
        "Ivanov",
        "Ivanovich",
        Email.create("ivan@example.com"),
        "hash",
    )

    assert user.id is None
    assert user.role is Role.USER
    assert user.full_name == "Ivanov Ivan Ivanovich"


def test_full_name_skips_a_missing_last_name() -> None:
    user = _user(last_name=None)

    assert user.full_name == "Ivanov Ivan"


def test_admin_can_be_reconstituted() -> None:
    user = _user(id=1, role=Role.ADMIN, last_name=None, first_name="Admin", surname="user")

    assert user.id == 1
    assert user.role is Role.ADMIN
    assert user.full_name == "user Admin"


def test_rename_keeps_omitted_fields() -> None:
    user = _user()

    user.rename(first_name="Petr")

    assert user.full_name == "Ivanov Petr Ivanovich"


def test_rename_can_clear_last_name() -> None:
    user = _user()

    user.rename(last_name=None)

    assert user.last_name is None
    assert user.full_name == "Ivanov Ivan"


def test_change_email_and_password() -> None:
    user = _user()
    email = Email.create("petr@example.com")

    user.change_email(email)
    user.change_password("new-hash")

    assert user.email == email
    assert user.password_hash == "new-hash"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("first_name", "  "),
        ("surname", ""),
        ("password_hash", ""),
    ],
)
def test_user_rejects_blank_required_fields(field: str, value: str) -> None:
    with pytest.raises(DomainValidationError):
        _user(**{field: value})
