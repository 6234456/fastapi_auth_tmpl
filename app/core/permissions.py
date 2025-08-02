from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
import uuid

from app.config import settings
from app.database import get_session
from app.models.user import User, Role
from app.schemas.auth import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """根据JWT令牌获取当前用户"""
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

        # 检查是否为访问令牌
        if token_data.type != "access":
            raise credentials_exception

        # 检查令牌是否过期
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = token_data.sub
    except JWTError:
        raise credentials_exception

    # 查询用户
    user = db.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户未激活")

    return user

async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前超级管理员用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要超级管理员权限",
        )
    return current_user

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
