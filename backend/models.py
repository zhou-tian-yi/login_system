from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    username = Column(String(50, collation="utf8mb4_bin"), unique=True, index=True, nullable=False)

    hashed_password = Column(String(256), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)