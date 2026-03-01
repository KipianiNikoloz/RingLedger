from fastapi import APIRouter

from app.api.bouts_routes.escrow_routes import router as escrow_router
from app.api.bouts_routes.payout_routes import router as payout_router
from app.api.bouts_routes.signing_routes import router as signing_router

router = APIRouter(prefix="/bouts")
router.include_router(escrow_router, tags=["bouts"])
router.include_router(payout_router, tags=["bouts"])
router.include_router(signing_router, tags=["bouts"])
