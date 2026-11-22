import pytest
from pydantic import SecretStr, ValidationError

from src.application.dtos.account import AccountOutput
from src.application.dtos.auth import AccessTokenOutput
from src.application.dtos.payment import PaymentOutput
from src.application.dtos.user import (
    UNSET,
    AccountBalanceOutput,
    UpdateUserInput,
    UserOutput,
    UserWithAccountsOutput,
)
from src.presentation.schemas.account import AccountResponse
from src.presentation.schemas.auth import TokenResponse
from src.presentation.schemas.payment import PaymentResponse, ProcessPaymentRequest
from src.presentation.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    UserWithAccountsResponse,
)


def test_user_responses_expose_fullname() -> None:
    user = UserResponse.from_output(
        UserOutput(id=2, email="ivan@example.com", full_name="Ivanov Ivan")
    )
    listed = UserWithAccountsResponse.from_output(
        UserWithAccountsOutput(
            id=2,
            email="ivan@example.com",
            full_name="Ivanov Ivan",
            accounts=(AccountBalanceOutput(id=1, balance=50),),
        )
    )

    assert user.model_dump() == {"id": 2, "email": "ivan@example.com", "fullname": "Ivanov Ivan"}
    assert listed.model_dump() == {
        "id": 2,
        "email": "ivan@example.com",
        "fullname": "Ivanov Ivan",
        "accounts": [{"id": 1, "balance": 50}],
    }


def test_account_and_payment_responses_keep_the_api_fields() -> None:
    account = AccountResponse.from_output(AccountOutput(id=1, user_id=2, balance=50))
    payment = PaymentResponse.from_output(
        PaymentOutput(
            id=7,
            amount=25,
            user_id=2,
            account_id=1,
            transaction_id="tx-1",
            signature="ab",
        )
    )
    token = TokenResponse.from_output(AccessTokenOutput(access_token="token"))

    assert account.model_dump() == {"id": 1, "user_id": 2, "balance": 50}
    assert payment.model_dump()["signature"] == "ab"
    assert token.model_dump() == {"access_token": "token", "token_type": "bearer"}


def test_create_user_request_unwraps_the_password() -> None:
    created = CreateUserRequest(
        first_name="Anna",
        surname="Smirnova",
        last_name=None,
        email="Anna@Example.com",
        password=SecretStr("password1"),
    ).to_input()

    assert created.email == "Anna@example.com"
    assert created.password == "password1"
    assert created.last_name is None


def test_update_request_distinguishes_omitted_last_name_from_null() -> None:
    omitted = UpdateUserRequest.model_validate({"first_name": "Petr"}).to_input()
    cleared = UpdateUserRequest.model_validate({"last_name": None}).to_input()
    password = UpdateUserRequest.model_validate({"password": "password1"}).to_input()

    assert omitted == UpdateUserInput(first_name="Petr")
    assert omitted.last_name is UNSET
    assert cleared.last_name is None
    assert password.password == "password1"


def test_empty_update_is_rejected() -> None:
    with pytest.raises(ValidationError, match="You must fill in at least one field"):
        UpdateUserRequest.model_validate({})


def test_payment_request_accepts_a_byte_signature() -> None:
    payload = ProcessPaymentRequest.model_validate(
        {
            "amount": 100,
            "user_id": 1,
            "account_id": 1,
            "transaction_id": "tx-1",
            "signature": bytes.fromhex("abcd"),
        }
    )

    assert payload.to_input().signature == "abcd"
