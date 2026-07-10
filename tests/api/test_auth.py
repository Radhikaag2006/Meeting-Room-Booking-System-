from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from tests.conftest import TEST_PASSWORD


# POST /auth/login


def test_login_success_super_admin(client, super_admin_user):
    resp = client.post(
        "/auth/login",
        json={"email": super_admin_user.email, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_success_office_admin(client, office_admin_user):
    resp = client.post(
        "/auth/login",
        json={"email": office_admin_user.email, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_success_employee(client, employee_user):
    resp = client.post(
        "/auth/login",
        json={"email": employee_user.email, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_wrong_password(client, employee_user):
    resp = client.post(
        "/auth/login",
        json={"email": employee_user.email, "password": "WrongPassword1"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@test.com", "password": TEST_PASSWORD},
    )
    assert resp.status_code == 404


def test_login_inactive_user(client, db_session, office):
    user = User(
        first_name="Inactive",
        last_name="Employee",
        email="inactive_employee@test.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=UserRole.EMPLOYEE,
        office_id=office.office_id,
        status=UserStatus.INACTIVE,
    )
    db_session.add(user)
    db_session.commit()

    resp = client.post(
        "/auth/login",
        json={"email": user.email, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 403


# GET /auth/me


def test_get_me_super_admin(client, super_admin_user, super_admin_headers):
    resp = client.get("/auth/me", headers=super_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == super_admin_user.email
    assert body["role"] == "SUPER_ADMIN"


def test_get_me_office_admin(client, office_admin_headers):
    resp = client.get("/auth/me", headers=office_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "OFFICE_ADMIN"


def test_get_me_employee(client, employee_headers):
    resp = client.get("/auth/me", headers=employee_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "EMPLOYEE"


def test_get_me_no_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_get_me_garbage_token(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer garbage-token"})
    assert resp.status_code == 401


# GET /auth/super-admin-test


def test_super_admin_test_allows_super_admin(client, super_admin_headers):
    resp = client.get("/auth/super-admin-test", headers=super_admin_headers)
    assert resp.status_code == 200


def test_super_admin_test_rejects_office_admin(client, office_admin_headers):
    resp = client.get("/auth/super-admin-test", headers=office_admin_headers)
    assert resp.status_code == 403


def test_super_admin_test_rejects_employee(client, employee_headers):
    resp = client.get("/auth/super-admin-test", headers=employee_headers)
    assert resp.status_code == 403


def test_super_admin_test_rejects_unauthenticated(client):
    resp = client.get("/auth/super-admin-test")
    assert resp.status_code == 401
