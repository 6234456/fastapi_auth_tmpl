from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, Role

def test_read_roles_as_admin(client: TestClient, admin_token: str, test_role: Role):
    # 测试管理员获取角色列表
    response = client.get(
        "/api/roles/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    role_names = [role["name"] for role in data]
    assert "testrole" in role_names

def test_read_roles_as_user(client: TestClient, user_token: str):
    # 测试普通用户获取角色列表（应该被拒绝）
    response = client.get(
        "/api/roles/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_create_role_as_admin(client: TestClient, admin_token: str):
    # 测试管理员创建新角色
    response = client.post(
        "/api/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "newrole",
            "description": "New Test Role",
            "permissions": {"permissions": ["new:permission"]}
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "newrole"
    assert data["description"] == "New Test Role"
    assert data["permissions"] == {"permissions": ["new:permission"]}

def test_read_role_as_admin(client: TestClient, admin_token: str, test_role: Role):
    # 测试管理员获取特定角色信息
    response = client.get(
        f"/api/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_role.id
    assert data["name"] == "testrole"

def test_update_role_as_admin(client: TestClient, admin_token: str, test_role: Role):
    # 测试管理员更新角色信息
    response = client.patch(
        f"/api/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "description": "Updated Test Role",
            "permissions": {"permissions": ["test:permission", "updated:permission"]}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Test Role"
    assert "updated:permission" in data["permissions"]["permissions"]

def test_delete_role_as_admin(client: TestClient, admin_token: str, test_role: Role):
    # 测试管理员删除角色
    response = client.delete(
        f"/api/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    # 确认角色已被删除
    response = client.get(
        f"/api/roles/{test_role.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404

def test_assign_role_to_user(client: TestClient, admin_token: str, test_user: User, session: Session):
    # 创建测试角色
    role_response = client.post(
        "/api/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "userrole",
            "description": "User Test Role",
            "permissions": {"permissions": ["user:permission"]}
        }
    )
    role_id = role_response.json()["id"]

    # 测试管理员为用户分配角色
    response = client.post(
        f"/api/users/{test_user.id}/roles/{role_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204

    # 验证角色分配成功
    response = client.get(
        f"/api/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.json()
    role_names = [role["name"] for role in data["roles"]]
    assert "userrole" in role_names
