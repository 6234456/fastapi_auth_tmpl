from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from pydantic import EmailStr

# 用户角色关联表（多对多关系）
class UserRoleLink(SQLModel, table=True):
    __tablename__ = "user_role_links"

    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    permissions: Dict[str, Any] = Field(sa_column=Column(JSON), default={})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系属性
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)  # 使用EmailStr进行验证
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系属性
    roles: List[Role] = Relationship(back_populates="users", link_model=UserRoleLink)
