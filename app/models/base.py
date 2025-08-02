from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

Base = declarative_base()

# 用户角色关联表（多对多关系）
user_role_link = Table(
    'user_role_links',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=lambda: datetime.now(timezone.utc))
)
