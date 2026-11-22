from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from src.application.dtos.user import AccountBalanceOutput, UserWithAccountsOutput
from src.infrastructure.db.guard import translate_errors
from src.infrastructure.db.models.account import AccountModel
from src.infrastructure.db.models.user import UserModel


class SqlAlchemyUsersWithAccountsQuery:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch(self) -> list[UserWithAccountsOutput]:
        stmt = (
            select(UserModel)
            .options(
                joinedload(UserModel.accounts).load_only(
                    AccountModel.id,
                    AccountModel.user_id,
                    AccountModel.balance,
                ),
                load_only(
                    UserModel.id,
                    UserModel.first_name,
                    UserModel.surname,
                    UserModel.last_name,
                    UserModel.email,
                ),
            )
            .order_by(UserModel.id)
        )
        result = await translate_errors(self._session.scalars(stmt))
        return [_to_output(user) for user in result.unique().all()]


def _to_output(user: UserModel) -> UserWithAccountsOutput:
    accounts = tuple(
        AccountBalanceOutput(id=account.id, balance=account.balance)
        for account in sorted(user.accounts, key=lambda account: account.id)
    )
    full_name = " ".join(
        part for part in (user.surname, user.first_name, user.last_name) if part
    )
    return UserWithAccountsOutput(
        id=user.id,
        email=user.email,
        full_name=full_name,
        accounts=accounts,
    )
