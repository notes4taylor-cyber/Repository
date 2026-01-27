"""
User management API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models.user import User
from app.core.security import get_current_user_id, get_password_hash

router = APIRouter()


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    artist_name: Optional[str] = None
    avatar_url: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str
    new_password: str


class UserStatsResponse(BaseModel):
    """Schema for user statistics."""
    tracks_mastered: int
    total_processing_time: float
    subscription_tier: str
    credits: float
    available_features: list


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user statistics and usage information.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserStatsResponse(
        tracks_mastered=user.tracks_mastered,
        total_processing_time=user.total_processing_time,
        subscription_tier=user.subscription_tier.value,
        credits=user.credits,
        available_features=user.available_features,
    )


@router.patch("/profile")
async def update_profile(
    update_data: UserUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile information.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.artist_name is not None:
        user.artist_name = update_data.artist_name
    if update_data.avatar_url is not None:
        user.avatar_url = update_data.avatar_url

    await db.commit()

    return {"message": "Profile updated successfully"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password.
    """
    from app.core.security import verify_password

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()

    return {"message": "Password changed successfully"}
