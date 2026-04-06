from pydantic import BaseModel


class AccountSchema(BaseModel):
    id: int
    balance: int
    user_id: int
