from sqlalchemy import Column, DateTime, ForeignKey, Table, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

# 用户角色关联表（多对多关系）
user_role_link = Table(
    'user_role_links',
    Base.metadata,
    Column('user_id',Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=lambda: datetime.now(timezone.utc))
)