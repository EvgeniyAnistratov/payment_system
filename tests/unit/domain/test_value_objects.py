import pytest

from src.domain.errors.base import DomainValidationError
from src.domain.value_objects.email import Email
from src.domain.value_objects.money import Money
from src.domain.value_objects.role import Role


def test_money_accepts_a_positive_amount() -> None:
    assert Money(1).value == 1
    assert Money(100).value == 100


@pytest.mark.parametrize("value", [0, -1])
def test_money_rejects_a_non_positive_amount(value: int) -> None:
    with pytest.raises(DomainValidationError, match="Amount must be positive"):
        Money(value)


def test_email_create_normalizes_the_address() -> None:
    email = Email.create("  Ivan@Example.com ")

    assert email.value == "ivan@example.com"


def test_email_create_rejects_an_invalid_address() -> None:
    with pytest.raises(DomainValidationError, match="Invalid email format: not-an-email"):
        Email.create("not-an-email")


def test_email_constructor_rejects_an_unnormalized_address() -> None:
    with pytest.raises(DomainValidationError, match="Invalid email format"):
        Email("Ivan@Example.com")


def test_role_values_match_the_database_enum() -> None:
    assert Role.ADMIN.value == "ADMIN"
    assert Role.USER.value == "USER"
