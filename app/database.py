from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import settings
import logging
from app.models.base import Base

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL, 
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
def create_db_and_tables():
    logger.info("创建数据库表...")
    try:
        # 导入所有模型以确保元数据被注册
        import app.models.user

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功!")
    except Exception as e:
        logger.error(f"创建数据库表时出错: {e}")
        raise

# Session 依赖
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
