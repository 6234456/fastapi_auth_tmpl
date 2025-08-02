# FastAPI 认证与授权系统

一个使用 FastAPI、SQLModel 和 JWT 实现的完整认证与授权后端系统。

## 功能特点

- 基于 FastAPI 的高性能异步 API
- 使用 SQLModel 作为 ORM，支持类型安全的数据操作
- JWT 认证系统，支持令牌刷新
- 基于角色的访问控制 (RBAC)
- 支持 SQLite 开发环境，可平滑迁移至 PostgreSQL 生产环境
- Alembic 数据库迁移支持
- 全面的测试覆盖

## 项目结构

```
fastapi-auth-project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── dependencies.py        # 依赖注入
│   ├── models/                # 数据模型
│   ├── schemas/               # Pydantic 模式
│   ├── crud/                  # 数据库操作
│   ├── api/                   # API 路由
│   ├── core/                  # 核心功能
│   └── utils/                 # 工具函数
├── alembic/                   # 数据库迁移
├── tests/                     # 测试文件
├── requirements.txt           # 依赖文件
└── .env                       # 环境变量
```

## 技术栈

- **FastAPI**: 现代化、高性能的 Web 框架
- **SQLModel**: 结合 SQLAlchemy 和 Pydantic 的 ORM
- **SQLite/PostgreSQL**: 数据库支持
- **JWT**: JSON Web Token 认证
- **Alembic**: 数据库迁移工具
- **PassLib**: 密码加密与验证
- **Pydantic**: 数据验证与序列化
- **Uvicorn**: ASGI 服务器

## 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/fastapi-auth-project.git
cd fastapi-auth-project
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或者
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 创建环境变量

创建 `.env` 文件并填入以下内容：

```
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./sql_app.db
```

### 5. 运行数据库迁移

```bash
alembic upgrade head
```

### 6. 启动应用

```bash
uvicorn app.main:app --reload
```

## API 文档

启动应用后，可以访问以下URL查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 认证流程

1. 用户注册: POST `/api/auth/register`
2. 用户登录: POST `/api/auth/login`
3. 使用返回的访问令牌访问受保护的API
4. 令牌过期后刷新: POST `/api/auth/refresh`

## 权限控制

系统基于角色的访问控制 (RBAC)：

- 超级管理员：拥有所有权限
- 管理员：用户和角色管理权限
- 普通用户：仅访问个人信息权限

## 迁移到 PostgreSQL

1. 更新 `.env` 文件中的 `DATABASE_URL`：

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

2. 运行数据库迁移：

```bash
alembic upgrade head
```

## 测试

运行测试套件：

```bash
python -m pytest
```

## 许可证

MIT
