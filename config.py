from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    LOGGING_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    SERVICE_URL: str

    model_config = SettingsConfigDict(
        env_file = Path(__file__).parent / ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()

import logging.config
from utils.logger import RequestIDFilter

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "filters": {
        "request_id_filter": {
            "()": RequestIDFilter,
        }
    },
    "handlers": {
        "default": {
            "level": settings.LOGGING_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "filters": ["request_id_filter"],
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(Path(__file__).parent / "logs" / "app.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["request_id_filter"],
        },
        "error": {
            "level": "ERROR",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(Path(__file__).parent / "logs" / "error.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 5,
            "encoding": "utf-8",
            "filters": ["request_id_filter"],
        }
    },
    "loggers": {
        "fastapi": {"handlers": ["default", "file", "error"], "level": "WARNING", "propagate": False},
        "uvicorn": {"handlers": ["default", "file", "error"], "level": "WARNING", "propagate": False},
        "app": {"handlers": ["default", "file", "error"], "level": "DEBUG", "propagate": False},
    },
}

log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")