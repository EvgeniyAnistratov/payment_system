from src.domain.entities.account import Account
from src.infrastructure.db.models.account import AccountModel


class AccountMapper:
    @staticmethod
    def to_domain(model: AccountModel) -> Account:
        return Account(id=model.id, user_id=model.user_id, balance=model.balance)

    @staticmethod
    def to_persistence(entity: Account) -> dict[str, object]:
        return {"id": entity.id, "user_id": entity.user_id, "balance": entity.balance}
