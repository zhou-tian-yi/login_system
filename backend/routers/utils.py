import logging
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from backend.database import get_db
from backend.utils.security import decode_token
import backend.models as models

logger = logging.getLogger("app")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        payload = decode_token(token)
        id = payload.get("sub")
        if id is None:
            logger.warning("Token 验证失败: 缺少 sub 字段")
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "无效的登录凭证",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        id = int(id)
        user = await find_user_by_id(id, db)
        if user is None or not user.is_active:
            logger.warning("Token 验证失败: 用户不存在或已注销，ID: %s", id)
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "无效的登录凭证",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        return user
    
    except jwt.ExpiredSignatureError:
        logger.info("Token 已过期")
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "凭证已过期，请重新登录",
            headers = {"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        logger.warning("Token 无效（签名验证失败或格式错误）")
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