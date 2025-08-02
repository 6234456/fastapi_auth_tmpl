from fastapi.testclient import TestClient
from app.models.user import User, Role

def test_read_me(client: TestClient, user_token: str):
    # 测试获取当前用户信息
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_update_me(client: TestClient, user_token: str):
    # 测试更新当前用户信息
    response = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"username": "updateduser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "test@example.com"

def test_read_users_as_admin(client: TestClient, admin_token: str, test_user: User):
    # 测试管理员获取用户列表
    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # 至少有管理员和测试用户
    usernames = [user["username"] for user in data]
    assert "testadmin" in usernames
    assert "testuser" in usernames or "updateduser" in usernames

def test_read_users_as_user(client: TestClient, user_token: str):
    # 测试普通用户获取用户列表（应该被拒绝）
    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_create_user_as_admin(client: TestClient, admin_token: str):
    # 测试管理员创建新用户
    response = client.post(
        "/api/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "username": "admincreatednewuser",
            "email": "admincreated@example.com",
            "password": "newpassword",
            "password_confirm": "newpassword"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "admincreatednewuser"
    assert data["email"] == "admincreated@example.com"

def test_read_user_as_admin(client: TestClient, admin_token: str, test_user: User):
    # 测试管理员获取特定用户信息
    response = client.get(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)

def test_read_user_self(client: TestClient, user_token: str, test_user: User):
    # 测试用户获取自己的信息
    response = client.get(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_user.id)

def test_read_user_other(client: TestClient, user_token: str, test_admin: User):
    # 测试普通用户获取其他用户信息（应该被拒绝）
    response = client.get(
        f"/api/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_update_user_as_admin(client: TestClient, admin_token: str, test_user: User):
    # 测试管理员更新用户信息
    response = client.patch(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"email": "updated@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"

def test_delete_user_as_admin(client: TestClient, admin_token: str, test_user: User):
    # 测试管理员删除用户
    response = client.delete(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    # 确认用户已被删除
    response = client.get(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
