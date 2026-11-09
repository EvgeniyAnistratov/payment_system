from src.domain.errors.base import DomainError


class AccountOwnershipMismatchError(DomainError):
    def __init__(self, account_id: int, payer_id: int) -> None:
        self.account_id = account_id
        self.payer_id = payer_id
        super().__init__(f"Account {account_id} does not belong to user {payer_id}")
