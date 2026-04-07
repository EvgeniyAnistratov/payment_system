from pydantic import BaseModel


class TokenScheme(BaseModel):
    access_token: str
    token_type: str
