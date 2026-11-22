from uuid import uuid4

from src.application.dtos.auth import AuthContext
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from src.infrastructure.config.settings import JwtSettings
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.services.jwt_access_token_issuer import JwtAccessTokenIssuer
from src.infrastructure.services.jwt_auth_context_resolver import JwtAuthContextResolver


async def test_issued_token_resolves_to_the_stored_user(db_session) -> None:
    repository = SqlAlchemyUserRepository(db_session)
    user = await repository.add(
        User(
            first_name="Ann",
            surname="Doe",
            last_name=None,
            email=Email.create(f"jwt-{uuid4()}@example.com"),
            password_hash="hash",
            role=Role.ADMIN,
        )
    )
    assert user.id is not None
    settings = JwtSettings()
    issuer = JwtAccessTokenIssuer(settings)
    resolver = JwtAuthContextResolver(settings, repository)

    resolved = await resolver.resolve(issuer.issue(user.id))

    assert resolved == AuthContext(user_id=user.id, role=Role.ADMIN)
    assert await resolver.resolve("not-a-token") is None
    assert await resolver.resolve(issuer.issue(999_999)) is None
