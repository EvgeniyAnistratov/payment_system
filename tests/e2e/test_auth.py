from tests.helpers.api import ADMIN_EMAIL, ADMIN_PASSWORD, USER_EMAIL, USER_PASSWORD, bearer


async def test_admin_and_user_can_log_in(client):
    admin = await client.post(
        "/auth/token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    user = await client.post(
        "/auth/token",
        data={"username": USER_EMAIL, "password": USER_PASSWORD},
    )

    assert admin.status_code == 200
    assert admin.json()["token_type"] == "bearer"
    assert admin.json()["access_token"]

    assert user.status_code == 200
    assert user.json()["token_type"] == "bearer"
    assert user.json()["access_token"]
    assert admin.json()["access_token"] != user.json()["access_token"]


async def test_login_rejects_unknown_email_and_wrong_password(client):
    unknown = await client.post(
        "/auth/token",
        data={"username": "missing@example.com", "password": USER_PASSWORD},
    )
    wrong_password = await client.post(
        "/auth/token",
        data={"username": USER_EMAIL, "password": "wrong_password"},
    )

    assert unknown.status_code == 401
    assert unknown.json()["detail"] == "Could not validate credentials"
    assert wrong_password.status_code == 401
    assert wrong_password.json()["detail"] == "Could not validate credentials"


async def test_missing_and_invalid_token_are_rejected(client):
    missing = await client.get("/users/2")
    invalid = await client.get("/users/2", headers=bearer("not-a-token"))

    assert missing.status_code == 401
    assert missing.json()["detail"] == "Not authenticated"
    assert invalid.status_code == 401
    assert invalid.json()["detail"] == "Could not validate credentials"
