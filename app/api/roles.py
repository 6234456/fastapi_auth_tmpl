from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Any, Optional, Dict
import uuid

from app.schemas.user import RoleRead, RoleCreate, RoleUpdate, RoleWithUsers
from app.database import get_session
from app.crud.user import (
    get_role, get_roles, create_role, update_role, delete_role,
    get_role_users
)
from app.core.permissions import check_role_management_permission
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[RoleRead])
async def read_roles(skip: int = 0, limit: int = 100, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_role_management_permission)):
    """获取角色列表（需要角色管理权限）"""
    return get_roles(db, skip=skip, limit=limit)

@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_new_role(role_data: RoleCreate, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_role_management_permission)):
    """创建新角色（需要角色管理权限）"""
    return create_role(
        db, 
        name=role_data.name, 
        description=role_data.description, 
        permissions=role_data.permissions
    )

@router.get("/{role_id}", response_model=RoleRead)
async def read_role(role_id: uuid.UUID, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_role_management_permission)):
    """获取特定角色信息（需要角色管理权限）"""
    role = get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role

@router.patch("/{role_id}", response_model=RoleRead)
async def update_specific_role(role_id: uuid.UUID, 
                            role_update: RoleUpdate,
                            db: Session = Depends(get_session),
                            _: User = Depends(check_role_management_permission)):
    """更新特定角色信息（需要角色管理权限）"""
    update_data = role_update.model_dump(exclude_unset=True)
    db_role = update_role(
        db, 
        role_id, 
        name=update_data.get("name"), 
        description=update_data.get("description"), 
        permissions=update_data.get("permissions")
    )
    if db_role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return db_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_specific_role(role_id: uuid.UUID, 
                            db: Session = Depends(get_session),
                            _: User = Depends(check_role_management_permission)):
    """删除特定角色（需要角色管理权限）"""
    success = delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"detail": "角色已删除"}

@router.get("/{role_id}/users", response_model=List[UserRead])
async def read_role_users(role_id: uuid.UUID, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_role_management_permission)):
    """获取拥有特定角色的用户列表（需要角色管理权限）"""
    role = get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return get_role_users(db, role_id)

@router.get("/with-users", response_model=List[RoleWithUsers])
async def read_roles_with_users(skip: int = 0, limit: int = 100, 
                            db: Session = Depends(get_session),
                            _: User = Depends(check_role_management_permission)):
    """获取角色列表，包含每个角色的用户（需要角色管理权限）"""
    return get_roles(db, skip=skip, limit=limit)
