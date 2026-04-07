from pydantic import BaseModel


class BaseAccountSheme(BaseModel):
    id: int
    balance: int


class AccountScheme(BaseAccountSheme):
    user_id: int
