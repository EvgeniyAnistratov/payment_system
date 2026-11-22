from src.application.dtos.payment import ProcessPaymentInput
from src.application.errors.invalid_signature import InvalidSignatureError
from src.application.ports.payment_signature_verifier import PaymentSignatureVerifier
from src.application.ports.transaction_manager import TransactionManager
from src.domain.entities.account import Account
from src.domain.entities.payment import Payment
from src.domain.errors.common import NotFoundError
from src.domain.repositories.account_repository import AccountRepository
from src.domain.repositories.payment_repository import PaymentRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.money import Money


class ProcessPaymentUseCase:
    def __init__(
        self,
        transaction_manager: TransactionManager,
        signature_verifier: PaymentSignatureVerifier,
        user_repository: UserRepository,
        account_repository: AccountRepository,
        payment_repository: PaymentRepository,
    ) -> None:
        self._transaction_manager = transaction_manager
        self._signature_verifier = signature_verifier
        self._user_repository = user_repository
        self._account_repository = account_repository
        self._payment_repository = payment_repository

    async def execute(self, data: ProcessPaymentInput) -> None:
        if not self._signature_verifier.verify(data):
            raise InvalidSignatureError("Invalid signature")

        amount = Money(data.amount)

        async with self._transaction_manager.transaction():
            if await self._user_repository.find_by_id(data.user_id) is None:
                raise NotFoundError(f"User {data.user_id} not found")

            await self._account_repository.add_if_absent(
                Account.open(data.account_id, data.user_id)
            )
            account = await self._account_repository.get_for_update(data.account_id)
            if account is None:
                raise NotFoundError(f"Account {data.account_id} not found")

            payment = Payment(
                external_id=data.transaction_id,
                user_id=data.user_id,
                account_id=data.account_id,
                amount=amount,
                signature=bytes.fromhex(data.signature),
            )
            if not await self._payment_repository.add_if_absent(payment):
                return

            account.deposit(amount, payer_id=data.user_id)
            await self._account_repository.save(account)
