from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from tests.helpers.api import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    USER_EMAIL,
    USER_PASSWORD,
    bearer,
    login,
)

ROOT = Path(__file__).resolve().parents[2]

RESET_SQL = """
DELETE FROM "transaction";
DELETE FROM account WHERE id <> 1;
INSERT INTO account (id, balance, user_id)
VALUES (1, 50, 2)
ON CONFLICT (id) DO UPDATE SET balance = 50, user_id = 2;
UPDATE users SET
    first_name = 'Admin',
    surname = 'user',
    last_name = NULL,
    email = 'admin@example.com',
    role = 'ADMIN'
WHERE id = 1;
UPDATE users SET
    first_name = 'Ivan',
    surname = 'Ivanov',
    last_name = 'Ivanovich',
    email = 'ivan@example.com',
    role = 'USER'
WHERE id = 2;
DELETE FROM users WHERE id NOT IN (1, 2);
"""


def _restore_seed(engine) -> None:
    from app.core.settings import DB_NAME

    if "test" not in DB_NAME:
        raise RuntimeError(
            f"Refusing to reset database {DB_NAME!r}: the name must contain 'test'"
        )

    with engine.begin() as connection:
        connection.execute(text(RESET_SQL))
        users = connection.execute(
            text("SELECT count(*) FROM users WHERE id IN (1, 2)")
        ).scalar_one()
        account = connection.execute(
            text("SELECT balance, user_id FROM account WHERE id = 1")
        ).one()

    if users != 2 or tuple(account) != (50, 2):
        raise RuntimeError(
            "Test database seed is missing. Recreate the test database and apply migrations."
        )


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
def sync_engine(apply_migrations):
    from app.core.settings import get_alembic_url

    engine = create_engine(get_alembic_url(), pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def reset_database(sync_engine):
    _restore_seed(sync_engine)
    yield


@pytest.fixture
async def client():
    from httpx import ASGITransport, AsyncClient

    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client


@pytest.fixture
async def admin_headers(client):
    token = await login(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    return bearer(token)


@pytest.fixture
async def user_headers(client):
    token = await login(client, USER_EMAIL, USER_PASSWORD)
    return bearer(token)
