import pytest

pytestmark = pytest.mark.asyncio


async def test_register_returns_token_pair(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123", "full_name": "Test User"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_register_duplicate_email_conflicts(client):
    payload = {"email": "dupe@example.com", "password": "SecurePass123", "full_name": "Dupe User"}
    first = await client.post("/api/v1/auth/register", json=payload)
    second = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


async def test_login_with_correct_credentials(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "SecurePass123", "full_name": "Login User"},
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "login@example.com", "password": "SecurePass123"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_with_wrong_password_fails(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "password": "SecurePass123", "full_name": "User"},
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "wrongpw@example.com", "password": "IncorrectPass"}
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "SecurePass123", "full_name": "Me User"},
    )
    token = register.json()["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"
    assert resp.json()["is_onboarded"] is False
