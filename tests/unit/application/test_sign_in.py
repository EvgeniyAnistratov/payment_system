import pytest

from src.application.dtos.auth import SignInInput
from src.application.use_cases.auth.sign_in import SignInUseCase
from src.domain.errors.auth import InvalidCredentialsError
from src.domain.value_objects.role import Role
from tests.helpers.factories import add_user, make_user
from tests.helpers.fakes.adapters import FakeAccessTokenIssuer, FakePasswordHasher
from tests.helpers.fakes.repositories import InMemoryUserRepository
from tests.helpers.fakes.store import InMemoryStore


def _use_case(store: InMemoryStore) -> SignInUseCase:
    return SignInUseCase(
        InMemoryUserRepository(store),
        FakePasswordHasher(),
        FakeAccessTokenIssuer(),
    )


async def test_sign_in_returns_a_bearer_token() -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2))

    token = await _use_case(store).execute(
        SignInInput(email="  Ivan@Example.com  ", password="user_password")
    )

    assert token.access_token == "token:2"
    assert token.token_type == "bearer"


@pytest.mark.parametrize(
    "email,password",
    [
        ("missing@example.com", "user_password"),
        ("ivan@example.com", "wrong"),
        ("not-an-email", "user_password"),
    ],
)
async def test_sign_in_rejects_bad_credentials(email: str, password: str) -> None:
    store = InMemoryStore()
    add_user(store, make_user(user_id=2, role=Role.USER))

    with pytest.raises(InvalidCredentialsError, match="Could not validate credentials"):
        await _use_case(store).execute(SignInInput(email=email, password=password))
