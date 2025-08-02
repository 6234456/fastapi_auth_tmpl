from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Any
import uuid

from app.schemas.user import UserRead, UserUpdate, UserCreate
from app.database import get_session
from app.crud.user import (
    get_user, get_users, create_user, update_user, delete_user,
    get_user_roles, assign_role_to_user, remove_role_from_user
)
from app.core.permissions import get_current_user, check_user_management_permission, get_current_active_superuser
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

@router.patch("/me", response_model=UserRead)
async def update_user_me(user_update: UserUpdate, 
                        current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_session)):
    """更新当前用户信息"""
    return update_user(db, current_user.id, user_update)

@router.get("/", response_model=List[UserRead])
async def read_users(skip: int = 0, limit: int = 100, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_user_management_permission)):
    """获取用户列表（需要用户管理权限）"""
    return get_users(db, skip=skip, limit=limit)

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(user_data: UserCreate, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """创建新用户（需要用户管理权限）"""
    return create_user(db, user_data)

@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: uuid.UUID, 
                    db: Session = Depends(get_session),
                    current_user: User = Depends(get_current_user)):
    """获取特定用户信息（用户本人或管理员）"""
    # 检查是否为用户本人或有管理权限
    if str(current_user.id) != str(user_id) and not current_user.is_superuser:
        # 检查是否拥有user:manage权限
        has_permission = False
        for role in current_user.roles:
            if "user:manage" in role.permissions.get("permissions", []):
                has_permission = True
                break

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )

    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_specific_user(user_id: uuid.UUID, 
                            user_update: UserUpdate,
                            db: Session = Depends(get_session),
                            _: User = Depends(check_user_management_permission)):
    """更新特定用户信息（需要用户管理权限）"""
    db_user = update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specific_user(user_id: uuid.UUID, 
                            db: Session = Depends(get_session),
                            _: User = Depends(get_current_active_superuser)):
    """删除特定用户（需要超级管理员权限）"""
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"detail": "用户已删除"}

@router.get("/{user_id}/roles", response_model=List[RoleRead])
async def read_user_roles(user_id: uuid.UUID, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """获取特定用户的角色列表（需要用户管理权限）"""
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return get_user_roles(db, user_id)

@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_user_role(user_id: uuid.UUID, 
                        role_id: uuid.UUID,
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """为用户分配角色（需要用户管理权限）"""
    success = assign_role_to_user(db, user_id, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户或角色不存在")
    return {"detail": "角色分配成功"}

@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_role(user_id: uuid.UUID, 
                        role_id: uuid.UUID,
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """移除用户的角色（需要用户管理权限）"""
    success = remove_role_from_user(db, user_id, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户或角色不存在，或用户未分配该角色")
    return {"detail": "角色移除成功"}
