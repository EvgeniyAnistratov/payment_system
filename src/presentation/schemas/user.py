from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator
from pydantic_core import PydanticCustomError

from src.application.dtos.user import (
    CreateUserInput,
    UpdateUserInput,
    UserOutput,
    UserWithAccountsOutput,
)
from src.presentation.schemas.account import AccountBalanceResponse


class CreateUserRequest(BaseModel):
    first_name: str = Field(examples=["Ivan"])
    surname: str = Field(examples=["Ivanov"])
    last_name: str | None = Field(examples=["Ivanovich"])
    email: EmailStr = Field(examples=["ivanov@example.com"])
    password: SecretStr = Field(examples=["secret_string"], min_length=8)

    def to_input(self) -> CreateUserInput:
        return CreateUserInput(
            first_name=self.first_name,
            surname=self.surname,
            last_name=self.last_name,
            email=str(self.email),
            password=self.password.get_secret_value(),
        )


class UpdateUserRequest(BaseModel):
    first_name: str | None = Field(default=None, examples=["Ivan"])
    surname: str | None = Field(default=None, examples=["Ivanov"])
    last_name: str | None = Field(default=None, examples=["Ivanovich"])
    email: EmailStr | None = Field(default=None, examples=["ivanov@example.com"])
    password: SecretStr | None = Field(default=None, examples=["secret_string"], min_length=8)

    @model_validator(mode="before")
    @classmethod
    def require_a_field(cls, data: object) -> object:
        if isinstance(data, dict) and not data:
            raise PydanticCustomError("body", "You must fill in at least one field.")
        return data

    def to_input(self) -> UpdateUserInput:
        raw = self.model_dump(exclude_unset=True)
        if isinstance(raw.get("password"), SecretStr):
            raw["password"] = raw["password"].get_secret_value()
        if raw.get("email") is not None:
            raw["email"] = str(raw["email"])
        return UpdateUserInput(**raw)


class UserResponse(BaseModel):
    id: int
    email: str
    fullname: str

    @classmethod
    def from_output(cls, output: UserOutput) -> "UserResponse":
        return cls(id=output.id, email=output.email, fullname=output.full_name)


class UserWithAccountsResponse(BaseModel):
    id: int
    email: str
    fullname: str
    accounts: list[AccountBalanceResponse]

    @classmethod
    def from_output(cls, output: UserWithAccountsOutput) -> "UserWithAccountsResponse":
        return cls(
            id=output.id,
            email=output.email,
            fullname=output.full_name,
            accounts=[AccountBalanceResponse.from_output(account) for account in output.accounts],
        )
