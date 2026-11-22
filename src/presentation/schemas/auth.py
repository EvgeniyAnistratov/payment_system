from pydantic import BaseModel

from src.application.dtos.auth import AccessTokenOutput


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    @classmethod
    def from_output(cls, output: AccessTokenOutput) -> "TokenResponse":
        return cls(access_token=output.access_token, token_type=output.token_type)
