from typing import AsyncIterable
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from payment_system.repositories import AccountRepo, TransactionRepo, UserRepo
from payment_system.services import AccountService, AuthService, TransactionService, UserService


class AppProvider(Provider):
    def __init__(self, uri: str, db_logging: bool):
        super().__init__(scope=Scope.APP)
        self.uri = uri
        self.db_logging = db_logging

    @provide
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(self.uri, echo=self.db_logging)

    @provide
    def get_session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_auth_service(self, user_repo: UserRepo) -> AuthService:
        return AuthService(user_repo)

    @provide(scope=Scope.REQUEST)
    def get_account_repo(self, session: AsyncSession) -> AccountRepo:
        return AccountRepo(session)

    @provide(scope=Scope.REQUEST)
    def get_account_service(self, account_repo: AccountRepo) -> AccountService:
        return AccountService(account_repo)

    @provide(scope=Scope.REQUEST)
    def get_transaction_repo(self, session: AsyncSession) -> TransactionRepo:
        return TransactionRepo(session)

    @provide(scope=Scope.REQUEST)
    def get_transaction_service(self, transaction_repo: TransactionRepo) -> TransactionService:
        return TransactionService(transaction_repo)

    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> UserRepo:
        return UserRepo(session)

    @provide(scope=Scope.REQUEST)
    def get_user_service(self, user_repo: UserRepo) -> UserService:
        return UserService(user_repo)
