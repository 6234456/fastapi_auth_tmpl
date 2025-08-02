from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
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


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True


class UserReadWithoutRoles(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 创建用户请求模式
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str
    is_active: bool = True

    @field_validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values.data and v != values.data['password']:
            raise ValueError('密码不匹配')
        return v

# 更新用户请求模式
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

# 角色响应模式
class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 用户响应模式（基本信息）
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# 用户详细响应模式（包含角色）
class UserDetailRead(UserRead):
    roles: List[RoleRead] = []

    model_config = ConfigDict(from_attributes=True)
# 角色带用户信息的模型
class RoleWithUsers(RoleRead):
    users: List[UserReadWithoutRoles] = []

    class Config:
        orm_mode = True
