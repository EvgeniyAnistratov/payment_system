from pydantic import BaseModel


class BaseAccountShema(BaseModel):
    id: int
    balance: int


class AccountSchema(BaseAccountShema):
    user_id: int
