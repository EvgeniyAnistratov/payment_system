from pydantic import BaseModel

from src.application.dtos.account import AccountOutput
from src.application.dtos.user import AccountBalanceOutput


class AccountBalanceResponse(BaseModel):
    id: int
    balance: int

    @classmethod
    def from_output(cls, output: AccountBalanceOutput) -> "AccountBalanceResponse":
        return cls(id=output.id, balance=output.balance)


class AccountResponse(BaseModel):
    id: int
    balance: int
    user_id: int

    @classmethod
    def from_output(cls, output: AccountOutput) -> "AccountResponse":
        return cls(id=output.id, balance=output.balance, user_id=output.user_id)
