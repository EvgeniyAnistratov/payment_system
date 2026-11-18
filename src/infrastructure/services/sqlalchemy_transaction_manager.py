from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyTransactionManager:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        try:
            yield
        except BaseException:
            await self._session.rollback()
            raise
        await self._session.commit()
