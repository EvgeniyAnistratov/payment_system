from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import DbSettings
from src.infrastructure.db.engine import create_engine

ROOT = Path(__file__).resolve().parents[2]


def _require_test_database() -> DbSettings:
    settings = DbSettings()
    if "test" not in settings.name:
        raise RuntimeError(
            f"Refusing to use database {settings.name!r}: the name must contain 'test'"
        )
    return settings


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    from alembic import command
    from alembic.config import Config

    config = Config(str(ROOT / "alembic.ini"))
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
async def engine(apply_migrations):
    db_engine = create_engine(_require_test_database())
    yield db_engine
    await db_engine.dispose()


@pytest.fixture
async def db_session(engine):
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
