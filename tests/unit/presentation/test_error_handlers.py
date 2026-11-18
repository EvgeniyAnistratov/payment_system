import pytest
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.dtos.auth import AuthContext
from src.application.errors.access_denied import AccessDeniedError
from src.application.errors.invalid_signature import InvalidSignatureError
from src.application.errors.repository import RepositoryError
from src.application.ports.auth_context_resolver import AuthContextResolver
from src.domain.errors.account import AccountOwnershipMismatchError
from src.domain.errors.auth import InvalidCredentialsError
from src.domain.errors.base import DomainValidationError
from src.domain.errors.common import AlreadyExistsError, NotFoundError
from src.domain.value_objects.role import Role
from src.presentation.dependencies.auth import CurrentActor
from src.presentation.error_handlers import register_error_handlers
from src.presentation.errors.unauthorized import UnauthorizedError


class _Resolver:
    def __init__(self, result: AuthContext | None) -> None:
        self.result = result

    async def resolve(self, token: str) -> AuthContext | None:
        return self.result


def _client(error: Exception) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/fail")
    async def fail() -> None:
        raise error

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    ("error", "status_code", "detail"),
    [
        (
            DomainValidationError("Amount must be positive"),
            400,
            "Amount must be positive",
        ),
        (
            InvalidCredentialsError("Could not validate credentials"),
            401,
            "Could not validate credentials",
        ),
        (InvalidSignatureError("Invalid signature"), 401, "Invalid signature"),
        (
            UnauthorizedError("Could not validate credentials"),
            401,
            "Could not validate credentials",
        ),
        (
            AccessDeniedError("You do not have permissions to do this action"),
            403,
            "You do not have permissions to do this action",
        ),
        (NotFoundError("User 9 not found"), 404, "User 9 not found"),
        (
            AlreadyExistsError("A user with email ivan@example.com already exists"),
            409,
            "A user with email ivan@example.com already exists",
        ),
        (
            AccountOwnershipMismatchError(1, 2),
            409,
            "Account 1 does not belong to user 2",
        ),
        (RepositoryError("Database operation failed"), 500, "Internal server error"),
    ],
)
def test_errors_map_to_http_statuses(error: Exception, status_code: int, detail: str) -> None:
    response = _client(error).get("/fail")

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}
    if status_code == 401:
        assert response.headers["www-authenticate"] == "Bearer"
    else:
        assert "www-authenticate" not in response.headers


class _ResolverProvider(Provider):
    def __init__(self, result: AuthContext | None) -> None:
        super().__init__(scope=Scope.APP)
        self._result = result

    @provide
    def resolver(self) -> AuthContextResolver:
        return _Resolver(self._result)


def _actor_client(result: AuthContext | None) -> TestClient:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/me")
    async def me(actor: CurrentActor) -> dict[str, object]:
        return {"user_id": actor.user_id, "role": actor.role.value}

    container = make_async_container(_ResolverProvider(result), FastapiProvider())
    setup_dishka(container, app)
    return TestClient(app, raise_server_exceptions=False)


def test_current_actor_reads_a_valid_token() -> None:
    client = _actor_client(AuthContext(user_id=2, role=Role.USER))

    with client:
        response = client.get("/me", headers={"Authorization": "Bearer token"})

    assert response.status_code == 200
    assert response.json() == {"user_id": 2, "role": "USER"}


def test_unknown_token_is_rejected() -> None:
    client = _actor_client(None)

    with client:
        response = client.get("/me", headers={"Authorization": "Bearer not-a-token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_missing_token_is_rejected() -> None:
    client = _actor_client(None)

    with client:
        response = client.get("/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
