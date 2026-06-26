import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from utils.logger import RequestIDMiddleware
from routers import router
from config import settings

logger = logging.getLogger("app")

app = FastAPI(
    title = "XX管理系统",
    description = "提供用于注册和登录的 API",
    version = "0.1.0"
)

app.add_middleware(RequestIDMiddleware)

app.include_router(router)

frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    errors = []
    for err in exc.errors():
        msg = err.get("msg", "参数格式错误")
        loc = err.get("loc", [])
        loc_str = " -> ".join(str(l) for l in loc)
        error_messages.append(f"[{loc_str}]: {msg}")
        errors.append({
            "location": loc,
            "message": msg,
            "type": err.get("type")
        })
    
    logger.warning(f"客户端请求参数校验失败! 错误详情: {'; '.join(error_messages)}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "message": "请求参数格式错误",
            "data": errors
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code = exc.status_code,
        content = {
            "message": exc.detail,
            "data": {}
        }
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    logger.exception("系统内部发生未捕获的异常！")
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误，请联系系统管理员",
            "data": {}
        }
    )



logger.info("应用启动完成，服务地址: %s", settings.SERVICE_URL)