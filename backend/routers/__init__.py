from fastapi import APIRouter
from . import auth, users

router = APIRouter(prefix="/api")

router.include_router(auth.router)
router.include_router(users.router)

@router.get("/")
async def health_check():
    return {
        "message": "正常运行中",
        "data": {}
    }