"""Tests for the authentication system."""

import pytest

from app.main import app, store
from app.user_models import UserStore
from app.auth import create_token, decode_token
from app.middleware import user_store


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        store._items.clear()
        user_store._users.clear()
        user_store._by_username.clear()
        yield client


@pytest.fixture
def registered_user(client):
    resp = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "secret123"},
    )
    return resp.get_json()


@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['token']}"}


class TestTokenCreation:
    def test_create_and_decode_token(self):
        token = create_token("user-123", "admin")
        payload = decode_token(token)
        assert payload is not None
        assert payload["user_id"] == "user-123"
        assert payload["role"] == "admin"

    def test_decode_invalid_token(self):
        assert decode_token("invalid.token.here") is None

    def test_decode_empty_token(self):
        assert decode_token("") is None


class TestRegistration:
    def test_register_success(self, client):
        resp = client.post(
            "/auth/register",
            json={"username": "newuser", "email": "new@test.com", "password": "pass123"},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["username"] == "newuser"

    def test_register_missing_fields(self, client):
        resp = client.post("/auth/register", json={"username": "only"})
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client):
        client.post(
            "/auth/register",
            json={"username": "dup", "email": "a@test.com", "password": "pass"},
        )
        resp = client.post(
            "/auth/register",
            json={"username": "dup", "email": "b@test.com", "password": "pass"},
        )
        assert resp.status_code == 409


class TestLogin:
    def test_login_success(self, client, registered_user):
        resp = client.post(
            "/auth/login", json={"username": "testuser", "password": "secret123"}
        )
        assert resp.status_code == 200
        assert "token" in resp.get_json()

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post(
            "/auth/login", json={"username": "testuser", "password": "wrong"}
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/auth/login", json={"username": "nobody", "password": "pass"}
        )
        assert resp.status_code == 401


class TestProfile:
    def test_profile_with_valid_token(self, client, auth_headers):
        resp = client.get("/auth/profile", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["user"]["username"] == "testuser"

    def test_profile_without_token(self, client):
        resp = client.get("/auth/profile")
        assert resp.status_code == 401

    def test_profile_with_invalid_token(self, client):
        resp = client.get(
            "/auth/profile", headers={"Authorization": "Bearer garbage"}
        )
        assert resp.status_code == 401


class TestPasswordHashing:
    def test_hash_password_produces_different_salts(self):
        hash1, salt1 = UserStore.hash_password("password")
        hash2, salt2 = UserStore.hash_password("password")
        assert salt1 != salt2
        assert hash1 != hash2

    def test_verify_correct_password(self):
        password_hash, salt = UserStore.hash_password("mypassword")
        verify_hash, _ = UserStore.hash_password("mypassword", salt)
        assert verify_hash == password_hash

    def test_verify_wrong_password(self):
        password_hash, salt = UserStore.hash_password("correct")
        verify_hash, _ = UserStore.hash_password("wrong", salt)
        assert verify_hash != password_hash
