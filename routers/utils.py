import logging
import jwt
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database import get_db
from utils.security import decode_token
import models

logger = logging.getLogger("app")

async def get_current_user(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    token = request.cookies.get("access_token")
    if not token:
        logger.warning("请求缺少 access_token cookie")
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "未登录",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    try:
        payload = decode_token(token)
        id = payload.get("sub")
        token_version = payload.get("token_version")
        if id is None or token_version is None:
            logger.warning("登录凭证验证失败: 缺少字段")
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "无效的登录凭证",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        id = int(id)
        user = await find_user_by_id(id, db)
        if user is None or not user.is_active:
            logger.warning("登录凭证验证失败: 用户不存在或已注销，ID: %s", id)
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "无效的登录凭证",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        if int(token_version) != user.token_version:
            logger.warning("登录凭证已过期")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="登录已过期，请重新登录",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user
    
    except jwt.ExpiredSignatureError:
        logger.info("登录凭证已过期")
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "登录已过期，请重新登录",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        logger.warning("登录凭证无效")
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "无效的登录凭证",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def find_user_by_username(username: str, db: AsyncSession):
    stmt = select(models.User).where(models.User.username == username)
    result = await db.execute(stmt)
    return result.scalars().first()

async def find_user_by_id(id:int, db: AsyncSession):
    user = await db.get(models.User, id)
    return user