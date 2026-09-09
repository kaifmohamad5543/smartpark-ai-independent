from sqlalchemy import select

from app.models.user import User
from app.utils.security import hash_password


USER_DATA = {
    "full_name": "Automated Test User",
    "email": "authtest@smartpark.com",
    "password": "SmartParkTest123!",
}


def register_user(client):
    return client.post(
        "/api/auth/register",
        json=USER_DATA,
    )


def login_user(client, email=None, password=None):
    return client.post(
        "/api/auth/login",
        json={
            "email": email or USER_DATA["email"],
            "password": password or USER_DATA["password"],
        },
    )


def test_register_user_successfully(client, db_session):
    response = register_user(client)

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == USER_DATA["full_name"]
    assert data["email"] == USER_DATA["email"]
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data
    assert "password" not in data

    user = db_session.scalar(
        select(User).where(
            User.email == USER_DATA["email"]
        )
    )

    assert user is not None
    assert user.hashed_password != USER_DATA["password"]
    assert user.hashed_password.startswith("$argon2")


def test_duplicate_registration_is_rejected(client):
    first_response = register_user(client)

    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/auth/register",
        json={
            **USER_DATA,
            "email": "AUTHTEST@SMARTPARK.COM",
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == (
        "An account with this email already exists."
    )


def test_login_returns_bearer_token(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 20
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_is_rejected(client):
    register_user(client)

    response = login_user(
        client,
        password="DefinitelyWrong123!",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid email or password."
    )


def test_authenticated_user_can_access_me(client):
    register_user(client)

    login_response = login_user(client)
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == USER_DATA["email"]
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/api/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid or expired authentication token."
    )


def test_inactive_user_cannot_login(
    client,
    db_session,
):
    register_user(client)

    user = db_session.scalar(
        select(User).where(
            User.email == USER_DATA["email"]
        )
    )

    user.is_active = False
    db_session.commit()

    response = login_user(client)

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "This user account is inactive."
    )


def test_standard_user_cannot_access_admin_route(client):
    register_user(client)

    token = login_user(
        client
    ).json()["access_token"]

    response = client.get(
        "/api/admin/parking/locations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Administrator access is required."
    )


def test_admin_user_can_access_admin_route(
    client,
    db_session,
):
    admin = User(
        full_name="Automated Test Administrator",
        email="admin.test@smartpark.com",
        hashed_password=hash_password(
            "SmartParkAdminTest123!"
        ),
        role="admin",
        is_active=True,
    )

    db_session.add(admin)
    db_session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "admin.test@smartpark.com",
            "password": "SmartParkAdminTest123!",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/admin/parking/locations",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
