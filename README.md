# XX管理系统

一个简单的用户认证系统练习项目，基于 FastAPI + 原生 HTML/JS，前后端分离架构。

## 技术栈

- **后端**: FastAPI + SQLAlchemy（异步）+ MySQL
- **前端**: 原生 HTML + JS（无框架）

## 功能

- 用户注册 / 登录（JWT + httpOnly Cookie 认证）
- 查看个人信息
- 修改用户名 / 修改密码
- 注销账号

## 项目结构

```
├── frontend/           # 前端静态文件（独立部署）
├── routers/            # API 路由
│   ├── auth.py         # 注册、登录、登出
│   └── users.py        # 用户信息、修改密码、修改用户名、注销
├── utils/              # 工具模块（日志、安全）
├── scripts/            # 脚本（建表等）
├── main.py             # 应用入口
├── config.py           # 配置管理
├── models.py           # 数据库模型
├── schemas.py          # Pydantic 请求/响应模型
└── run.py              # 启动脚本
```

## 环境要求

- Python 3.10+
- MySQL 8.0+

## 快速开始

### 1. 创建数据库

```sql
CREATE DATABASE auth_system CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的数据库连接信息、JWT 密钥和服务地址：

```
DATABASE_URL = mysql+aiomysql://root:你的密码@localhost:3306/auth_system
JWT_KEY = 随便填一串随机字符
SERVICE_URL = http://127.0.0.1:8000
ALLOW_ORIGINS = ["http://127.0.0.1:5500"]
```

> **注意**：`ALLOW_ORIGINS` 需与前端的实际访问地址一致。
> 不要使用 `localhost`，因为 `SameSite=Lax` Cookie 策略下 `localhost` 与 `127.0.0.1` 被视为不同站点，会导致认证失败。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 创建数据表

```bash
python -m scripts.create_tables
```

### 5. 启动后端服务

```bash
python run.py
```

后端 API 运行在 `http://127.0.0.1:8000`。

### 6. 启动前端服务

新开一个终端窗口，执行：

```bash
python -m http.server 5500 -d frontend
```

浏览器访问 `http://127.0.0.1:5500` 即可使用系统。
