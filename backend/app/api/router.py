from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.bouts import router as bouts_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(bouts_router)
