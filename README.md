# XX管理系统

一个简单的用户认证系统练习项目，基于 FastAPI + 原生 HTML/JS。

## 技术栈

- **后端**: FastAPI + SQLAlchemy（异步）+ MySQL
- **前端**: 原生 HTML + JS（无框架）

## 功能

- 用户注册 / 登录（JWT + httpOnly Cookie 认证）
- 查看个人信息
- 修改用户名 / 修改密码
- 注销账号

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
cd backend
cp .env.example .env
```

编辑 `.env`，填入你的数据库连接信息、JWT 密钥和服务地址：

```
DATABASE_URL = mysql+aiomysql://root:你的密码@localhost:3306/auth_system
JWT_KEY = 随便填一串随机字符
SERVICE_URL = http://127.0.0.1:8000
```

### 3. 安装依赖

```bash
pip install -r backend/requirements.txt
```

### 4. 创建数据表

```bash
cd backend
python -m backend.scripts.create_tables
```

### 5. 启动服务

```bash
cd backend
python run.py
```

浏览器访问服务地址（默认 `http://127.0.0.1:8000`）
