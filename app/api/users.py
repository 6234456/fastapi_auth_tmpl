from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.user import get_user, get_users, update_user, delete_user, assign_role_to_user, remove_role_from_user
from app.schemas.user import UserRead, UserDetailRead, UserUpdate
from app.database import get_session
from app.core.permissions import get_current_user, get_current_active_superuser, check_user_management_permission
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserDetailRead)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return current_user

@router.put("/me", response_model=UserRead)
async def update_user_me(user_update: UserUpdate, 
                        current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_session)):
    """更新当前登录用户信息"""
    return update_user(db, current_user.id, user_update)

@router.get("/", response_model=List[UserRead])
async def read_users(skip: int = 0, 
                    limit: int = 100, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_user_management_permission)):
    """获取用户列表（需要管理权限）"""
    return get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserDetailRead)
async def read_user(user_id: int, 
                    db: Session = Depends(get_session),
                    current_user: User = Depends(get_current_user)):
    """获取特定用户信息"""
    # 检查权限：只允许超级管理员或用户本人
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限访问此用户信息"
        )

    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.put("/{user_id}", response_model=UserRead)
async def update_user_endpoint(user_id: int, 
                        user_update: UserUpdate, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """更新用户信息（需要管理权限）"""
    db_user = update_user(db, user_id, user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: int, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """删除用户（需要管理权限）"""
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="用户不存在")
@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def assign_user_role(user_id: int, 
                        role_id: int,
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """为用户分配角色（需要用户管理权限）"""
    success = assign_role_to_user(db, user_id, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户或角色不存在")
    return {"detail": "角色分配成功"}

@router.delete("/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_role(user_id: int, 
                        role_id: int,
                        db: Session = Depends(get_session),
                        _: User = Depends(check_user_management_permission)):
    """移除用户的角色（需要用户管理权限）"""
    success = remove_role_from_user(db, user_id, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户或角色不存在，或用户未分配该角色")
    return {"detail": "角色移除成功"}
