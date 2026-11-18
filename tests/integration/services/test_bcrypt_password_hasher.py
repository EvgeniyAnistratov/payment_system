import asyncio
import importlib.util
from pathlib import Path

import bcrypt
import pytest

from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher

_SEED_MIGRATION = (
    Path(__file__).resolve().parents[3] / "migrations" / "versions" / "8ac482ce4e25_mock_data.py"
)


def _seed_migration():
    spec = importlib.util.spec_from_file_location("seed_migration", _SEED_MIGRATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def test_hash_and_verify_roundtrip() -> None:
    hasher = BcryptPasswordHasher()

    hashed = await hasher.hash("secret")

    assert hashed != "secret"
    assert await hasher.verify("secret", hashed) is True
    assert await hasher.verify("other", hashed) is False


async def test_hash_and_verify_run_in_a_worker_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []
    original = asyncio.to_thread

    async def spy(func, /, *args, **kwargs):
        calls.append(func)
        return await original(func, *args, **kwargs)

    monkeypatch.setattr(
        "src.infrastructure.services.bcrypt_password_hasher.asyncio.to_thread",
        spy,
    )
    hasher = BcryptPasswordHasher()
    hashed = await hasher.hash("secret")

    assert await hasher.verify("secret", hashed) is True
    assert len(calls) == 2


def test_seed_password_hashes_match_the_documented_passwords() -> None:
    migration = _seed_migration()

    assert bcrypt.checkpw(b"admin_password", migration.ADMIN_PASSWORD_HASH.encode())
    assert bcrypt.checkpw(b"user_password", migration.USER_PASSWORD_HASH.encode())
