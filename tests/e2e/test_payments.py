import asyncio

import pytest

from tests.helpers.payments import payment_payload


async def _accounts(client, headers, user_id: int) -> list[dict]:
    response = await client.get(f"/users/{user_id}/accounts", headers=headers)
    assert response.status_code == 200, response.text
    return sorted(response.json(), key=lambda account: account["id"])


async def _transactions(client, headers, user_id: int) -> list[dict]:
    response = await client.get(f"/users/{user_id}/transactions", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


async def test_user_sees_own_accounts_and_admin_can_see_them_too(
    client, user_headers, admin_headers
):
    own = await _accounts(client, user_headers, 2)
    as_admin = await _accounts(client, admin_headers, 2)
    foreign = await client.get("/users/1/accounts", headers=user_headers)

    assert own == [{"id": 1, "balance": 50, "user_id": 2}]
    assert as_admin == own
    assert foreign.status_code == 403


async def test_transaction_list_starts_empty_and_is_private(client, user_headers, admin_headers):
    own = await _transactions(client, user_headers, 2)
    as_admin = await _transactions(client, admin_headers, 2)
    anonymous = await client.get("/users/2/transactions")
    forbidden = await client.get("/users/1/transactions", headers=user_headers)

    assert own == []
    assert as_admin == []
    assert anonymous.status_code == 401
    assert forbidden.status_code == 403


async def test_payment_increases_existing_account_balance(client, user_headers):
    payload = payment_payload(user_id=2, account_id=1, amount=25)

    response = await client.post("/transactions", json=payload)

    assert response.status_code == 201
    assert response.content == b""
    assert await _accounts(client, user_headers, 2) == [{"id": 1, "balance": 75, "user_id": 2}]
    transactions = await _transactions(client, user_headers, 2)
    assert len(transactions) == 1
    saved = transactions[0]
    assert saved["transaction_id"] == payload["transaction_id"]
    assert saved["amount"] == 25
    assert saved["account_id"] == 1
    assert saved["user_id"] == 2
    assert saved["signature"] == payload["signature"]
    assert isinstance(saved["id"], int)


async def test_payment_with_invalid_signature_changes_nothing(client, user_headers):
    payload = payment_payload(
        user_id=2,
        account_id=1,
        amount=25,
        signature="0" * 64,
    )

    response = await client.post("/transactions", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid signature"
    assert await _accounts(client, user_headers, 2) == [{"id": 1, "balance": 50, "user_id": 2}]
    assert await _transactions(client, user_headers, 2) == []


async def test_duplicate_transaction_id_is_applied_once(client, user_headers):
    payload = payment_payload(user_id=2, account_id=1, amount=25)

    first = await client.post("/transactions", json=payload)
    second = await client.post("/transactions", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert await _accounts(client, user_headers, 2) == [{"id": 1, "balance": 75, "user_id": 2}]
    transactions = await _transactions(client, user_headers, 2)
    assert [item["transaction_id"] for item in transactions] == [payload["transaction_id"]]


async def test_payment_creates_missing_account_for_the_user(client, user_headers):
    payload = payment_payload(user_id=2, account_id=77, amount=40)

    response = await client.post("/transactions", json=payload)

    assert response.status_code == 201
    assert await _accounts(client, user_headers, 2) == [
        {"id": 1, "balance": 50, "user_id": 2},
        {"id": 77, "balance": 40, "user_id": 2},
    ]
    transactions = await _transactions(client, user_headers, 2)
    assert len(transactions) == 1
    assert transactions[0]["account_id"] == 77
    assert transactions[0]["amount"] == 40
    assert transactions[0]["transaction_id"] == payload["transaction_id"]


@pytest.mark.xfail(
    reason="unknown user_id is swallowed and the webhook returns 201",
    strict=False,
)
async def test_payment_for_unknown_user_is_not_found(client, admin_headers):
    payload = payment_payload(user_id=99999, account_id=88, amount=40)

    response = await client.post("/transactions", json=payload)

    assert response.status_code == 404
    assert await _accounts(client, admin_headers, 99999) == []
    assert await _transactions(client, admin_headers, 99999) == []
    assert await _accounts(client, admin_headers, 2) == [{"id": 1, "balance": 50, "user_id": 2}]


@pytest.mark.xfail(
    reason="concurrent payments for a new account can lose a payment and still return 201",
    strict=False,
)
async def test_parallel_payments_on_a_new_account_are_all_applied(client, user_headers):
    amounts = [10, 15, 20, 25, 30, 35, 40, 45]
    # Several fresh accounts: one burst can slip through without overlapping,
    # and the lost payment only happens when two inserts race.
    account_ids = (5001, 5002, 5003, 5004)
    payloads_by_account = {
        account_id: [
            payment_payload(user_id=2, account_id=account_id, amount=amount) for amount in amounts
        ]
        for account_id in account_ids
    }

    for account_id, payloads in payloads_by_account.items():
        responses = await asyncio.gather(
            *[client.post("/transactions", json=payload) for payload in payloads]
        )
        assert [response.status_code for response in responses] == [201] * len(amounts)

    accounts = {account["id"]: account for account in await _accounts(client, user_headers, 2)}
    saved = await _transactions(client, user_headers, 2)
    for account_id, payloads in payloads_by_account.items():
        assert accounts[account_id]["balance"] == sum(amounts)
        assert accounts[account_id]["user_id"] == 2
        saved_ids = {item["transaction_id"] for item in saved if item["account_id"] == account_id}
        assert saved_ids == {payload["transaction_id"] for payload in payloads}


@pytest.mark.xfail(
    reason="B4: a payment is credited to an account owned by another user",
    strict=False,
)
async def test_payment_to_someone_elses_account_is_rejected(client, admin_headers, user_headers):
    payload = payment_payload(user_id=1, account_id=1, amount=100)

    response = await client.post("/transactions", json=payload)

    assert response.status_code == 409
    assert await _accounts(client, user_headers, 2) == [{"id": 1, "balance": 50, "user_id": 2}]
    assert await _accounts(client, admin_headers, 1) == []
    assert await _transactions(client, admin_headers, 1) == []
    assert await _transactions(client, user_headers, 2) == []
