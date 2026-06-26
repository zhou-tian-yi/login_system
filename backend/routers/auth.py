import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from config import settings
from database import get_db
from utils.security import get_password_hash, verify_password, create_access_token
import schemas
import models
from .utils import find_user_by_username

logger = logging.getLogger("app")

router = APIRouter(prefix="/auth", tags=["用户认证"])

@router.post("/register")
async def register(user: schemas.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    logger.info("收到注册请求，用户名: %s", user.username)

    user_db = await find_user_by_username(user.username, db)
    if user_db:
        logger.warning("注册失败，用户名已存在: %s", user.username)
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "用户名已存在"
        )
    
    hashed_pwd = get_password_hash(user.password)

    new_user = models.User(
        username = user.username,
        hashed_password = hashed_pwd
    )

    db.add(new_user)
    await db.commit()

    logger.info("注册成功，用户名: %s，用户ID: %s", user.username, new_user.id)
    return {
        "message": "注册成功",
        "data": {
            "id": new_user.id
        }
    }

@router.post("/login")
async def login(user: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]):
    logger.info("收到登录请求，用户名: %s", user.username)

    user_db = await find_user_by_username(user.username, db)
    if user_db is None or not user_db.is_active or not verify_password(user.password, user_db.hashed_password):
        logger.warning("登录失败，用户名或密码错误: %s", user.username)
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": str(user_db.id)})

    logger.info("登录成功，用户名: %s，用户ID: %s", user.username, user_db.id)
    response = JSONResponse({
        "message": "登录成功",
        "data": {}
    })
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response

@router.post("/logout")
async def logout():
    response = JSONResponse({"message": "已退出登录", "data": {}})
    response.delete_cookie(key="access_token")
    return response