ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin_password"
USER_EMAIL = "ivan@example.com"
USER_PASSWORD = "user_password"


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def login(client, email: str, password: str) -> str:
    response = await client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    return body["access_token"]
