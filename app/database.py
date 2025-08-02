from sqlmodel import SQLModel, create_engine, Session
from .config import settings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 创建所有表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Session 依赖
def get_session():
    with Session(engine) as session:
        yield session
