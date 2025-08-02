from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.crud.user import get_role, get_roles, create_role, update_role, delete_role, get_role_users, assign_role_to_user, remove_role_from_user
from app.schemas.user import RoleRead, UserRead, RoleUpdate, RoleWithUsers
from app.database import get_session
from app.core.permissions import check_role_management_permission
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[RoleRead])
async def read_roles(skip: int = 0, 
                    limit: int = 100, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_role_management_permission)):
    """获取角色列表（需要角色管理权限）"""
    return get_roles(db, skip=skip, limit=limit)

@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(name: str, 
                        description: Optional[str] = None, 
                        permissions: Dict[str, Any] = {}, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_role_management_permission)):
    """创建新角色（需要角色管理权限）"""
    return create_role(db, name, description, permissions)

@router.get("/{role_id}", response_model=RoleRead)
async def read_role(role_id: int, 
                   db: Session = Depends(get_session),
                   _: User = Depends(check_role_management_permission)):
    """获取特定角色信息（需要角色管理权限）"""
    db_role = get_role(db, role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return db_role

@router.put("/{role_id}", response_model=RoleRead)
async def update_role_endpoint(role_id: int, 
                        name: Optional[str] = None, 
                        description: Optional[str] = None, 
                        permissions: Optional[Dict[str, Any]] = None, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_role_management_permission)):
    """更新角色信息（需要角色管理权限）"""
    db_role = update_role(db, role_id, name, description, permissions)
    if db_role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return db_role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_endpoint(role_id: int, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_role_management_permission)):
    """删除角色（需要角色管理权限）"""
    if not delete_role(db, role_id):
        raise HTTPException(status_code=404, detail="角色不存在")

@router.get("/{role_id}/users", response_model=List[UserRead])
async def read_role_users(role_id: int, 
                        db: Session = Depends(get_session),
                        _: User = Depends(check_role_management_permission)):
    """获取具有特定角色的用户列表（需要角色管理权限）"""
    return get_role_users(db, role_id)

@router.post("/{role_id}/users/{user_id}", status_code=status.HTTP_200_OK)
async def assign_role(role_id: int, 
                    user_id: int, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_role_management_permission)):
    """为用户分配角色（需要角色管理权限）"""
    if not assign_role_to_user(db, user_id, role_id):
        raise HTTPException(status_code=404, detail="用户或角色不存在")
    return {"message": "角色分配成功"}

@router.delete("/{role_id}/users/{user_id}", status_code=status.HTTP_200_OK)
async def remove_role(role_id: int, 
                    user_id: int, 
                    db: Session = Depends(get_session),
                    _: User = Depends(check_role_management_permission)):
    """从用户移除角色（需要角色管理权限）"""
    if not remove_role_from_user(db, user_id, role_id):
        raise HTTPException(status_code=404, detail="用户、角色或关联不存在")
    return {"message": "角色移除成功"}
@router.get("/{role_id}", response_model=RoleRead)
async def read_role(role_id: int,
                    db: Session = Depends(get_session),
                    _: User = Depends(check_role_management_permission)):
    """获取特定角色信息（需要角色管理权限）"""
    role = get_role(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role

@router.patch("/{role_id}", response_model=RoleRead)
async def update_specific_role(role_id: int, 
                            role_update: RoleUpdate,
                            db: Session = Depends(get_session),
                            _: User = Depends(check_role_management_permission)):
    """更新特定角色信息（需要角色管理权限）"""
    update_data = role_update.dict(exclude_unset=True)
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
async def delete_specific_role(role_id: int, 
                            db: Session = Depends(get_session),
                            _: User = Depends(check_role_management_permission)):
    """删除特定角色（需要角色管理权限）"""
    success = delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="角色不存在")
    return {"detail": "角色已删除"}

@router.get("/{role_id}/users", response_model=List[UserRead])
async def read_role_users(role_id: int, 
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
