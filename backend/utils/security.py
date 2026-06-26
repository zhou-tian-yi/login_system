import logging
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from backend.config import settings

logger = logging.getLogger("app")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password) 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    jwt_code = jwt.encode(payload, settings.JWT_KEY, algorithm=ALGORITHM)
    logger.info("已创建 Access Token，sub: %s，有效期至: %s", data.get("sub"), expire.isoformat())
    return jwt_code

def decode_token(token: str):
    payload = jwt.decode(token, settings.JWT_KEY, algorithms=[ALGORITHM])
    return payload