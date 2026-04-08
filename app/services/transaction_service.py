from fastapi import HTTPException, Response, status
from sqlalchemy.exc import DatabaseError

from app.models import Transaction
from app.models.account import Account
from app.repositories import AccountRepo, TransactionRepo
from app.schemas import TransactionSchema
from app.core.settings import APP_TRANSACTION_SECRET
from app.utils.signature import check_singature


class TransactionService:
    def __init__(self, account_repo: AccountRepo, transaction_repo: TransactionRepo):
        """
        AccountRepo and TransactionRepo share the same session object
        because the Session dependency has the Scope.REQUEST property.
        """
        self.account_repo: AccountRepo = account_repo
        self.transaction_repo: TransactionRepo = transaction_repo

    async def get_list_by_user_id(self, user_id: int):
        accounts = await self.transaction_repo.get_by_user_id(user_id)
        return [TransactionSchema.model_validate(obj, from_attributes=True) for obj in accounts]

    async def process_transaction(self, transaction: TransactionSchema):
        payload = transaction.model_dump()
        signature = payload.pop("signature")

        if not check_singature(payload, signature, APP_TRANSACTION_SECRET):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )

        await self._save_transaction(transaction)

        return Response(status_code=status.HTTP_201_CREATED)

    async def _save_transaction(self, transaction: TransactionSchema):
        try:
            if await self.transaction_repo.get_by_transaction_id(transaction.transaction_id) is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Transaction with id {transaction.transaction_id} already exists"
                )

            account = await self.account_repo.select_for_update(transaction.account_id)
            if account is None:
                new_account = Account(
                    id=transaction.account_id,
                    balance=0,
                    user_id=transaction.user_id
                )
                await self.account_repo.create(new_account)
                await self.account_repo.commit()

                account = await self.account_repo.select_for_update(transaction.account_id)
                if account is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unexpected error occurred while processing a transaction"
                    )

            new_transaction = Transaction(
                amount=transaction.amount,
                user_id=transaction.user_id,
                account_id=transaction.account_id,
                transaction_id=transaction.transaction_id,
                signature=bytes.fromhex(transaction.signature)
            )
            await self.transaction_repo.create(new_transaction)

            account.balance += new_transaction.amount

            await self.transaction_repo.commit()
        except DatabaseError as e:
            await self.transaction_repo.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error occurred while processing a transaction"
            )
