import pytest

from tests.helpers.api import USER_EMAIL

SEEDED_USERS = [
    {
        "id": 1,
        "email": "admin@example.com",
        "fullname": "user Admin",
        "accounts": [],
    },
    {
        "id": 2,
        "email": "ivan@example.com",
        "fullname": "Ivanov Ivan Ivanovich",
        "accounts": [{"id": 1, "balance": 50}],
    },
]

NEW_USER = {
    "first_name": "Anna",
    "surname": "Smirnova",
    "last_name": None,
    "email": "anna@example.com",
    "password": "password1",
}


async def test_admin_lists_users_with_accounts(client, admin_headers):
    response = await client.get("/users", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == SEEDED_USERS


async def test_user_cannot_list_users(client, user_headers):
    response = await client.get("/users", headers=user_headers)

    assert response.status_code == 403
    assert "do not have permissions" in response.json()["detail"]


async def test_user_reads_own_profile_and_cannot_read_another(client, user_headers, admin_headers):
    own = await client.get("/users/2", headers=user_headers)
    foreign = await client.get("/users/1", headers=user_headers)
    as_admin = await client.get("/users/2", headers=admin_headers)

    assert own.status_code == 200
    assert own.json() == {
        "id": 2,
        "email": USER_EMAIL,
        "fullname": "Ivanov Ivan Ivanovich",
    }
    assert foreign.status_code == 403
    assert as_admin.status_code == 200
    assert as_admin.json() == own.json()


async def test_missing_user_returns_404(client, admin_headers):
    response = await client.get("/users/99999", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


async def test_admin_creates_user_and_duplicate_email_conflicts(client, admin_headers):
    created = await client.post("/users", json=NEW_USER, headers=admin_headers)
    duplicate = await client.post("/users", json=NEW_USER, headers=admin_headers)

    assert created.status_code == 200
    body = created.json()
    assert body["email"] == NEW_USER["email"]
    assert body["fullname"] == "Smirnova Anna"
    assert isinstance(body["id"], int)

    fetched = await client.get(f"/users/{body['id']}", headers=admin_headers)
    assert fetched.status_code == 200
    assert fetched.json() == body

    listed = await client.get("/users", headers=admin_headers)
    created_row = next(user for user in listed.json() if user["id"] == body["id"])
    assert created_row["accounts"] == []

    logged_in = await client.post(
        "/auth/token",
        data={"username": NEW_USER["email"], "password": NEW_USER["password"]},
    )
    assert logged_in.status_code == 200

    assert duplicate.status_code == 409
    assert NEW_USER["email"] in duplicate.json()["detail"]


async def test_user_cannot_create_update_or_delete_users(client, user_headers):
    create = await client.post("/users", json=NEW_USER, headers=user_headers)
    update = await client.patch("/users/2", json={"first_name": "Petr"}, headers=user_headers)
    delete = await client.delete("/users/2", headers=user_headers)

    assert create.status_code == 403
    assert update.status_code == 403
    assert delete.status_code == 403


async def test_admin_updates_user_name_and_leaves_omitted_last_name(client, admin_headers):
    response = await client.patch(
        "/users/2",
        json={"first_name": "Petr"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "email": USER_EMAIL,
        "fullname": "Ivanov Petr Ivanovich",
    }


async def test_admin_updates_email_to_a_free_address(client, admin_headers):
    response = await client.patch(
        "/users/2",
        json={"email": "ivan.petrov@example.com"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == "ivan.petrov@example.com"
    assert response.json()["fullname"] == "Ivanov Ivan Ivanovich"


async def test_empty_update_is_rejected(client, admin_headers):
    response = await client.patch("/users/2", json={}, headers=admin_headers)

    assert response.status_code == 422


async def test_update_and_delete_of_missing_user_return_404(client, admin_headers):
    update = await client.patch(
        "/users/99999",
        json={"first_name": "Petr"},
        headers=admin_headers,
    )
    delete = await client.delete("/users/99999", headers=admin_headers)

    assert update.status_code == 404
    assert delete.status_code == 404


@pytest.mark.xfail(reason="DELETE /users/{id} does not commit, so the user stays", strict=False)
async def test_admin_delete_removes_user(client, admin_headers):
    created = await client.post("/users", json=NEW_USER, headers=admin_headers)
    assert created.status_code == 200
    user_id = created.json()["id"]

    deleted = await client.delete(f"/users/{user_id}", headers=admin_headers)
    fetched = await client.get(f"/users/{user_id}", headers=admin_headers)

    assert deleted.status_code == 204
    assert fetched.status_code == 404


@pytest.mark.xfail(reason="PATCH with a taken email returns 500 instead of 409", strict=False)
async def test_update_to_taken_email_conflicts(client, admin_headers):
    response = await client.patch(
        "/users/2",
        json={"email": "admin@example.com"},
        headers=admin_headers,
    )
    profile = await client.get("/users/2", headers=admin_headers)

    assert response.status_code == 409
    assert profile.status_code == 200
    assert profile.json()["email"] == USER_EMAIL


@pytest.mark.xfail(
    reason="explicit null last_name is treated as an omitted field",
    strict=False,
)
async def test_update_can_clear_last_name(client, admin_headers):
    response = await client.patch(
        "/users/2",
        json={"last_name": None},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["fullname"] == "Ivanov Ivan"
    assert response.json()["email"] == USER_EMAIL
