import logging
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

logger = logging.getLogger("app")

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping = True
)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        except (HTTPException, RequestValidationError):
            raise
        except Exception:
            await db.rollback()
            logger.exception("数据库会话发生异常，已回滚")
            raise