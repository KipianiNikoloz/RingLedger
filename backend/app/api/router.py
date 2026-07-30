from fastapi import APIRouter

from app.api.admin_users import router as admin_users_router
from app.api.auth import router as auth_router
from app.api.bouts import router as bouts_router
from app.api.bouts_routes.management_routes import router as bout_management_router
from app.api.fighters import router as fighters_router

api_router = APIRouter()
api_router.include_router(admin_users_router)
api_router.include_router(auth_router)
api_router.include_router(fighters_router)
api_router.include_router(bout_management_router)
api_router.include_router(bouts_router)
