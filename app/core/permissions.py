from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone

from app.config.settings import settings
from app.database import get_session
from app.models.user import User, Role
from app.schemas.auth import TokenPayload

# OAuth2 密码流依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的身份验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        # 检查令牌类型
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌类型",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查令牌是否过期
        if datetime.fromtimestamp(token_data.exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取用户ID
        user_id = token_data.sub
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 从数据库中获取用户信息
    stmt = select(User).where(User.id == int(user_id))
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活"
        )

    return user

async def get_current_active_superuser(current_user: User = Depends(get_current_user)):
    """获取当前超级管理员用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限执行此操作"
        )
    return current_user

def has_role(role_name: str):
    """检查用户是否拥有特定角色"""
    async def _has_role(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
        # 超级管理员拥有所有权限
        if current_user.is_superuser:
            return current_user

        # 查询指定角色
        stmt = select(Role).where(Role.name == role_name)
        result = db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色 '{role_name}' 不存在"
            )

        # 检查用户是否拥有该角色
        user_roles = [r.name for r in current_user.roles]
        if role_name not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有足够的权限执行此操作"
            )

        return current_user

    return _has_role

def has_permission(permission: str):
    """检查用户是否具有特定权限的装饰器"""
    async def permission_dependency(current_user: User = Depends(get_current_user)):
        # 超级管理员拥有所有权限
        if current_user.is_superuser:
            return current_user

        # 检查用户角色中的权限
        for role in current_user.roles:
            role_permissions = role.permissions.get("permissions", [])
            if permission in role_permissions:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"权限不足，需要 {permission} 权限",
        )

    return permission_dependency

# 预定义的权限检查函数
def check_user_management_permission(current_user: User = Depends(has_permission("user:manage"))):
    return current_user

def check_role_management_permission(current_user: User = Depends(has_permission("role:manage"))):
    return current_user

def check_self_profile_permission(current_user: User = Depends(get_current_user)):
    return current_user
