from contextlib import AbstractAsyncContextManager
from typing import Protocol


class TransactionManager(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]: ...
