# creating a separate database for testing it so that data does notinterfere with our actual db

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env.test", override=True)

import pytest
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.office import Office
from app.models.user import User, UserRole, UserStatus

TEST_PASSWORD = "Test@1234"


@pytest.fixture(scope="session")
def test_engine():
    from app.core.database import engine

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def db_session(test_engine):
    connection = test_engine.connect()
    outer_trans = connection.begin()
    TestingSessionLocal = sessionmaker(bind=connection)
    session = TestingSessionLocal()
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    outer_trans.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Role / user fixtures

@pytest.fixture()
def office(db_session):
    o = Office(
        office_name="Test Office",
        address="123 Main St",
        city="Metropolis",
        state="NY",
        country="USA",
    )
    db_session.add(o)
    db_session.commit()
    db_session.refresh(o)
    return o


@pytest.fixture()
def other_office(db_session):
    o = Office(
        office_name="Other Office",
        address="456 Side St",
        city="Gotham",
        state="NJ",
        country="USA",
    )
    db_session.add(o)
    db_session.commit()
    db_session.refresh(o)
    return o


def _make_user(db_session, *, role, email, office_id=None, status=UserStatus.ACTIVE):
    user = User(
        first_name="Test",
        last_name=role.value.title(),
        email=email,
        password_hash=hash_password(TEST_PASSWORD),
        role=role,
        office_id=office_id,
        status=status,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def super_admin_user(db_session):
    return _make_user(db_session, role=UserRole.SUPER_ADMIN, email="super_admin@test.com")


@pytest.fixture()
def office_admin_user(db_session, office):
    return _make_user(
        db_session,
        role=UserRole.OFFICE_ADMIN,
        office_id=office.office_id,
        email="office_admin@test.com",
    )


@pytest.fixture()
def other_office_admin_user(db_session, other_office):
    return _make_user(
        db_session,
        role=UserRole.OFFICE_ADMIN,
        office_id=other_office.office_id,
        email="other_office_admin@test.com",
    )


@pytest.fixture()
def employee_user(db_session, office):
    return _make_user(
        db_session,
        role=UserRole.EMPLOYEE,
        office_id=office.office_id,
        email="employee@test.com",
    )


def _auth_headers(client, email):
    resp = client.post("/auth/login", json={"email": email, "password": TEST_PASSWORD})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def super_admin_headers(client, super_admin_user):
    return _auth_headers(client, super_admin_user.email)


@pytest.fixture()
def office_admin_headers(client, office_admin_user):
    return _auth_headers(client, office_admin_user.email)


@pytest.fixture()
def other_office_admin_headers(client, other_office_admin_user):
    return _auth_headers(client, other_office_admin_user.email)


@pytest.fixture()
def employee_headers(client, employee_user):
    return _auth_headers(client, employee_user.email)
