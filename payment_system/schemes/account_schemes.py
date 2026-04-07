from pydantic import BaseModel


class AccountScheme(BaseModel):
    id: int
    balance: int
    user_id: int
