from pydantic import BaseModel, EmailStr, UUID4, validator, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any] = {}

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None

class RoleRead(RoleBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str

    @validator("password_confirm")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("密码不匹配")
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserRead(UserBase):
    id: UUID4
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    roles: List[RoleRead] = []

    class Config:
        from_attributes = True

class UserReadWithoutRoles(UserBase):
    id: UUID4
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 角色带用户信息的模型
class RoleWithUsers(RoleRead):
    users: List[UserReadWithoutRoles] = []

    class Config:
        from_attributes = True
