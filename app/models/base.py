from sqlalchemy import Column, String, Boolean, JSON, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

# 自定义 UUID 类型，兼容 SQLite 和 PostgreSQL
class UUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

Base = declarative_base()

# 用户角色关联表（多对多关系）
user_role_link = Table(
    'user_role_links',
    Base.metadata,
    Column('user_id', UUID, ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=lambda: datetime.now(timezone.utc))
)