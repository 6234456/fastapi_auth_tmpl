from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey, Table,Integer
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.models.base import Base, user_role_link, UUID

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    permissions = Column(JSON, default={})
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系属性
    users = relationship("User", secondary=user_role_link, back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系属性
    roles = relationship("Role", secondary=user_role_link, back_populates="users")


# 为了兼容现有代码，添加 UserRoleLink 类
class UserRoleLink:
    """用户角色关联类，用于 CRUD 操作中的类型提示"""
    user_id: int
    role_id: int
