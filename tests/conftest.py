import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typing import Generator

from app.main import app
from app.database import get_session
from app.models.user import User, Role, UserRoleLink
from app.core.security import get_password_hash
import uuid

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="test_admin")
def test_admin_fixture(session: Session):
    admin = User(
        id=uuid.uuid4(),
        username="testadmin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin

@pytest.fixture(name="test_role")
def test_role_fixture(session: Session):
    role = Role(
        id=uuid.uuid4(),
        name="testrole",
        description="Test Role",
        permissions={"permissions": ["test:permission"]}
    )
    session.add(role)
    session.commit()
    session.refresh(role)
    return role

@pytest.fixture(name="admin_token")
def admin_token_fixture(client: TestClient, test_admin: User):
    response = client.post(
        "/api/auth/login",
        data={"username": "testadmin", "password": "adminpassword"}
    )
    return response.json()["access_token"]

@pytest.fixture(name="user_token")
def user_token_fixture(client: TestClient, test_user: User):
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]
