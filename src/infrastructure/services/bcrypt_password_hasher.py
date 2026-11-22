import asyncio

import bcrypt


class BcryptPasswordHasher:
    async def hash(self, raw_password: str) -> str:
        return await asyncio.to_thread(_hash_password, raw_password)

    async def verify(self, raw_password: str, password_hash: str) -> bool:
        return await asyncio.to_thread(_verify_password, raw_password, password_hash)


def _hash_password(raw_password: str) -> str:
    hashed = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt())
    return hashed.decode()


def _verify_password(raw_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(raw_password.encode(), password_hash.encode())
