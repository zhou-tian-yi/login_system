import logging
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database import get_db
import schemas as schemas
import models as models
from utils.security import verify_password, get_password_hash
from .utils import get_current_user, find_user_by_username

logger = logging.getLogger("app")

router = APIRouter(prefix="/users", tags=["用户"])

@router.get("/me")
async def get_me(user: Annotated[models.User, Depends(get_current_user)]):
    logger.info("查询用户信息，用户: %s (ID: %s)", user.username, user.id)
    return {
        "message": "请求成功",
        "data": {
            "username": user.username,
            "id": user.id,
            "created_at": user.created_at,
        }
    }

@router.delete("/me")
async def delete_account(payload: schemas.Password, user: Annotated[models.User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    logger.info("收到注销请求，用户: %s (ID: %s)", user.username, user.id)
    if not verify_password(payload.password, user.hashed_password):
        logger.warning("注销失败，密码错误，用户: %s (ID: %s)", user.username, user.id)
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "密码错误"
        )
    user.is_active = False
    user.username = f"{user.username}#delete#{int(time.time())}"
    await db.commit()
    logger.info("用户已成功注销，原用户名: %s (ID: %s)", user.username, user.id)
    return {
        "message": "用户已成功注销",
        "data": {}
    }

@router.post("/change-password")
async def change_password(payload: schemas.ChangePassword, user: Annotated[models.User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    logger.info("收到修改密码请求，用户: %s (ID: %s)", user.username, user.id)
    if payload.new_password == payload.old_password:
        logger.warning("修改密码失败，新旧密码相同，用户: %s (ID: %s)", user.username, user.id)
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "新密码不能与原密码相同"
        )
    if not verify_password(payload.old_password, user.hashed_password):
        logger.warning("修改密码失败，原密码错误，用户: %s (ID: %s)", user.username, user.id)
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "原密码错误"
        )
    user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()

    logger.info("密码修改成功，用户: %s (ID: %s)", user.username, user.id)
    return {
        "message": "密码修改成功",
        "data": {}
    }

@router.post("/change-username")
async def change_username(payload: schemas.ChangeUsername, user: Annotated[models.User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    logger.info("收到修改用户名请求，用户: %s (ID: %s)，新用户名: %s", user.username, user.id, payload.new_username)
    old_user = await find_user_by_username(payload.new_username, db)
    if old_user and old_user.id != user.id:
        logger.warning("修改用户名失败，目标用户名已被占用: %s", payload.new_username)
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "用户名已存在"
        )
    old_username = user.username
    user.username = payload.new_username
    await db.commit()

    logger.info("用户名修改成功，%s -> %s (ID: %s)", old_username, payload.new_username, user.id)
    return {
        "message": "用户名修改成功",
        "data": {}
    }