import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.utils.security import hash_password, verify_password

client = TestClient(app)


def test_register_user_success():
    email = f"user{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Akshay Mohan",
        "email": email,
        "password": "Password@123",
    }

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["full_name"] == payload["full_name"]
    assert data["email"] == payload["email"]


def test_long_password_hash_and_verify():
    long_password = "a" * 200
    hashed = hash_password(long_password)

    assert isinstance(hashed, str)
    assert verify_password(long_password, hashed) is True


def test_register_user_allows_long_passwords():
    email = f"user{uuid.uuid4().hex[:8]}@example.com"
    long_password = "a" * 200
    payload = {
        "full_name": "Long Password User",
        "email": email,
        "password": long_password,
    }

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201, response.text
    assert response.json()["email"] == email
