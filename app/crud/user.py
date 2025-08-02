from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional, Dict, Any, Union

from app.models.user import User, Role, UserRoleLink
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

# 用户相关CRUD操作
def get_user(db: Session, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    result = db.execute(select(User).where(User.email == email))
    return result.scalars().first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = db.execute(select(User).where(User.username == username))
    return result.scalars().first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """获取用户列表"""
    result = db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

def create_user(db: Session, user_create: UserCreate) -> User:
    """创建新用户"""
    # 创建用户对象
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        is_active=user_create.is_active
    )

    # 添加到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    # 获取用户
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # 更新字段
    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    # 保存更改
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """删除用户"""
    # 获取用户
    db_user = get_user(db, user_id)
    if not db_user:
        return False

    # 删除用户
    db.delete(db_user)
    db.commit()

    return True

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户身份"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# 角色相关CRUD操作
def get_role(db: Session, role_id: int) -> Optional[Role]:
    """根据ID获取角色"""
    result = db.execute(select(Role).where(Role.id == role_id))
    return result.scalars().first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    """根据名称获取角色"""
    result = db.execute(select(Role).where(Role.name == name))
    return result.scalars().first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """获取角色列表"""
    result = db.execute(select(Role).offset(skip).limit(limit))
    return result.scalars().all()

def create_role(db: Session, name: str, description: Optional[str] = None, permissions: Dict[str, Any] = {}) -> Role:
    """创建新角色"""
    # 创建角色对象
    db_role = Role(
        name=name,
        description=description,
        permissions=permissions
    )

    # 添加到数据库
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return db_role

def update_role(db: Session, role_id: int, name: Optional[str] = None,
                description: Optional[str] = None, permissions: Optional[Dict[str, Any]] = None) -> Optional[Role]:
    """更新角色信息"""
    # 获取角色
    db_role = get_role(db, role_id)
    if not db_role:
        return None

    # 更新字段
    if name is not None:
        db_role.name = name
    if description is not None:
        db_role.description = description
    if permissions is not None:
        db_role.permissions = permissions

    # 保存更改
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    return db_role

def delete_role(db: Session, role_id: int) -> bool:
    """删除角色"""
    # 获取角色
    db_role = get_role(db, role_id)
    if not db_role:
        return False

    # 删除角色
    db.delete(db_role)
    db.commit()

    return True

# 用户角色关联操作
def assign_role_to_user(db: Session, user_id: int, role_id: int) -> bool:
    """为用户分配角色"""
    # 检查用户和角色是否存在
    user = get_user(db, user_id)
    role = get_role(db, role_id)
    if not user or not role:
        return False

    # 检查是否已分配
    result = db.execute(
        select(UserRoleLink).where(
            UserRoleLink.user_id == user_id,
            UserRoleLink.role_id == role_id
        )
    )
    existing_link = result.scalars().first()

    if existing_link:
        return True  # 已经分配过，视为成功

    # 创建新的关联
    link = UserRoleLink()
    db.add(link)
    db.commit()

    return True

def remove_role_from_user(db: Session, user_id: int, role_id: int) -> bool:
    """从用户移除角色"""
    # 检查用户和角色是否存在
    user = get_user(db, user_id)
    role = get_role(db, role_id)
    if not user or not role:
        return False

    # 查找关联
    result = db.execute(
        select(UserRoleLink).where(
            UserRoleLink.user_id == user_id,
            UserRoleLink.role_id == role_id
        )
    )
    link = result.scalars().first()

    if not link:
        return False  # 未找到关联

    # 删除关联
    db.delete(link)
    db.commit()

    return True

def get_user_roles(db: Session, user_id: int) -> List[Role]:
    """获取用户的所有角色"""
    user = get_user(db, user_id)
    if not user:
        return []

    return user.roles

def get_role_users(db: Session, role_id: int) -> List[User]:
    """获取拥有特定角色的所有用户"""
    role = get_role(db, role_id)
    if not role:
        return []

    return role.users
