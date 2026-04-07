from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator
from pydantic_core import PydanticCustomError

from .account_schemes import BaseAccountSheme


class CreateUserScheme(BaseModel):
    first_name: str = Field(examples=["Ivan"])
    surname: str = Field(examples=["Ivanov"])
    last_name: str | None = Field(examples=["Ivanovich"])
    email: EmailStr = Field(examples=["ivanov@example.com"])
    password: SecretStr = Field(examples=["secret_string"], min_length=8)


class UpdateUserScheme(BaseModel):
    first_name: Optional[str] = Field(default=None, examples=["Ivan"])
    surname: Optional[str] = Field(default=None, examples=["Ivanov"])
    last_name: Optional[str | None] = Field(default=None, examples=["Ivanovich"])
    email: Optional[EmailStr] = Field(default=None, examples=["ivanov@example.com"])
    password: Optional[SecretStr] = Field(default=None, examples=["secret_string"], min_length=8)

    @model_validator(mode='before')
    def validate(self):
        values = [v for _, v in self.items()]
        if all(v is None for v in values):
            raise PydanticCustomError("body", "You must fill in at least one field.")
        return self


class UserScheme(BaseModel):
    id: int
    email: EmailStr
    fullname: str


class UserWithAccountScheme(UserScheme):
    accounts: List[BaseAccountSheme]
