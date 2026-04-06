from pydantic import BaseModel


class TransactionSchema(BaseModel):
    id: int
    amount: int
    user_id: int
    account_id: int
    transaction_id: str
