from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.database import create_db_and_tables
from app.config import settings
from app.api import auth, users, roles
from app.crud.user import create_role, assign_role_to_user, create_user, get_role_by_name, get_user_by_username
from app.schemas.user import UserCreate
from sqlmodel import Session
from app.database import get_session
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_db_and_tables()

    # 初始化默认角色和超级管理员
    try:
        db = Session(next(get_session.dependencies[0].dependency()))

        # 创建默认角色
        admin_role = get_role_by_name(db, "admin")
        if not admin_role:
            admin_role = create_role(
                db, 
                name="admin", 
                description="管理员角色", 
                permissions={
                    "permissions": ["user:manage", "role:manage"]
                }
            )
            logger.info("Created admin role")

        user_role = get_role_by_name(db, "user")
        if not user_role:
            create_role(
                db, 
                name="user", 
                description="普通用户角色", 
                permissions={
                    "permissions": ["profile:read", "profile:update"]
                }
            )
            logger.info("Created user role")

        # 创建超级管理员
        admin_user = get_user_by_username(db, "admin")
        if not admin_user:
            admin_user = create_user(
                db, 
                UserCreate(
                    username="admin",
                    email="admin@example.com",
                    password="adminpassword",
                    password_confirm="adminpassword",
                    is_active=True
                )
            )
            # 设置为超级管理员
            admin_user.is_superuser = True
            db.add(admin_user)
            db.commit()
            logger.info("Created superadmin user")

        # 为管理员分配管理员角色
        if admin_user and admin_role:
            assign_role_to_user(db, admin_user.id, admin_role.id)
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
    finally:
        db.close()

    yield
    # 应用关闭时清理资源
    pass

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI JWT认证与授权系统",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["认证"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["用户"])
app.include_router(roles.router, prefix=f"{settings.API_PREFIX}/roles", tags=["角色"])

@app.get("/")
async def root():
    return {"message": "欢迎使用FastAPI JWT认证系统"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
