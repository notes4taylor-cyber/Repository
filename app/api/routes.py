"""
API Routes for MasterFlow.
"""
from fastapi import APIRouter

from app.api import auth, tracks, mastering, users, pricing

router = APIRouter()

# Include sub-routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(tracks.router, prefix="/tracks", tags=["Tracks"])
router.include_router(mastering.router, prefix="/mastering", tags=["Mastering"])
router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])
