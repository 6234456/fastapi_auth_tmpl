from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User

def test_register_user(client: TestClient):
    # 测试注册新用户
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword",
            "password_confirm": "newpassword"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_register_duplicate_username(client: TestClient, test_user: User):
    # 测试注册重复用户名
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "newpassword",
            "password_confirm": "newpassword"
        }
    )
    assert response.status_code == 400
    assert "用户名已被使用" in response.json()["detail"]

def test_register_duplicate_email(client: TestClient, test_user: User):
    # 测试注册重复邮箱
    response = client.post(
        "/api/auth/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "newpassword",
            "password_confirm": "newpassword"
        }
    )
    assert response.status_code == 400
    assert "邮箱已被注册" in response.json()["detail"]

def test_login_success(client: TestClient, test_user: User):
    # 测试登录成功
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user: User):
    # 测试登录密码错误
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]

def test_login_inactive_user(client: TestClient, session: Session, test_user: User):
    # 将用户设为非活动
    test_user.is_active = False
    session.add(test_user)
    session.commit()

    # 测试登录非活动用户
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert "用户未激活" in response.json()["detail"]

def test_refresh_token(client: TestClient, test_user: User):
    # 先登录获取刷新令牌
    login_response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # 测试刷新令牌
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
