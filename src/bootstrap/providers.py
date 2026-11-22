from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.ports.access_token_issuer import AccessTokenIssuer
from src.application.ports.auth_context_resolver import AuthContextResolver
from src.application.ports.password_hasher import PasswordHasher
from src.application.ports.payment_signature_verifier import PaymentSignatureVerifier
from src.application.ports.queries.users_with_accounts_query import UsersWithAccountsQuery
from src.application.ports.transaction_manager import TransactionManager
from src.application.use_cases.accounts.list_user_accounts import ListUserAccountsUseCase
from src.application.use_cases.auth.sign_in import SignInUseCase
from src.application.use_cases.payments.list_user_payments import ListUserPaymentsUseCase
from src.application.use_cases.payments.process_payment import ProcessPaymentUseCase
from src.application.use_cases.users.create_user import CreateUserUseCase
from src.application.use_cases.users.delete_user import DeleteUserUseCase
from src.application.use_cases.users.get_user import GetUserUseCase
from src.application.use_cases.users.list_users_with_accounts import ListUsersWithAccountsUseCase
from src.application.use_cases.users.update_user import UpdateUserUseCase
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.payment_repository import PaymentRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.config.settings import AppSettings, DbSettings, JwtSettings
from src.infrastructure.db.engine import create_engine, create_session_factory
from src.infrastructure.repositories.sqlalchemy_account_repository import (
    SqlAlchemyAccountRepository,
)
from src.infrastructure.repositories.sqlalchemy_payment_repository import (
    SqlAlchemyPaymentRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.repositories.sqlalchemy_users_with_accounts_query import (
    SqlAlchemyUsersWithAccountsQuery,
)
from src.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.services.jwt_access_token_issuer import JwtAccessTokenIssuer
from src.infrastructure.services.jwt_auth_context_resolver import JwtAuthContextResolver
from src.infrastructure.services.sha256_payment_signature import Sha256PaymentSignature
from src.infrastructure.services.sqlalchemy_transaction_manager import SqlAlchemyTransactionManager


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def db_settings(self) -> DbSettings:
        return DbSettings()

    @provide
    def jwt_settings(self) -> JwtSettings:
        return JwtSettings()

    @provide
    def app_settings(self) -> AppSettings:
        return AppSettings()


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, settings: DbSettings) -> AsyncEngine:
        return create_engine(settings)

    @provide(scope=Scope.APP)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            yield session


class AdapterProvider(Provider):
    scope = Scope.REQUEST

    user_repository = provide(SqlAlchemyUserRepository, provides=UserRepository)
    account_repository = provide(SqlAlchemyAccountRepository, provides=AccountRepository)
    payment_repository = provide(SqlAlchemyPaymentRepository, provides=PaymentRepository)
    users_with_accounts_query = provide(
        SqlAlchemyUsersWithAccountsQuery,
        provides=UsersWithAccountsQuery,
    )
    transaction_manager = provide(
        SqlAlchemyTransactionManager,
        provides=TransactionManager,
    )
    auth_context_resolver = provide(
        JwtAuthContextResolver,
        provides=AuthContextResolver,
    )

    password_hasher = provide(
        BcryptPasswordHasher,
        provides=PasswordHasher,
        scope=Scope.APP,
    )
    token_issuer = provide(
        JwtAccessTokenIssuer,
        provides=AccessTokenIssuer,
        scope=Scope.APP,
    )
    signature_verifier = provide(
        Sha256PaymentSignature,
        provides=PaymentSignatureVerifier,
        scope=Scope.APP,
    )


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    sign_in = provide(SignInUseCase)
    create_user = provide(CreateUserUseCase)
    get_user = provide(GetUserUseCase)
    update_user = provide(UpdateUserUseCase)
    delete_user = provide(DeleteUserUseCase)
    list_users_with_accounts = provide(ListUsersWithAccountsUseCase)
    list_user_accounts = provide(ListUserAccountsUseCase)
    list_user_payments = provide(ListUserPaymentsUseCase)
    process_payment = provide(ProcessPaymentUseCase)
