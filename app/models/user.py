"""
User model for authentication and account management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base


class SubscriptionTier(enum.Enum):
    """User subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    ADVANCED = "advanced"
    PRO = "pro"
    UNLIMITED = "unlimited"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    artist_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)

    # Credits (for pay-per-track users)
    credits = Column(Float, default=0.0)

    # Usage tracking
    tracks_mastered = Column(Integer, default=0)
    total_processing_time = Column(Float, default=0.0)  # seconds

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    tracks = relationship("Track", back_populates="user", cascade="all, delete-orphan")
    mastering_jobs = relationship("MasteringJob", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def can_master(self) -> bool:
        """Check if user can master tracks."""
        if self.subscription_tier == SubscriptionTier.UNLIMITED:
            return True
        if self.subscription_tier == SubscriptionTier.FREE:
            return self.credits > 0 or self.tracks_mastered < 1  # 1 free track
        return self.credits > 0

    @property
    def available_features(self) -> list:
        """Get list of available features for user's tier."""
        features = ["basic_mastering", "mp3_output"]

        if self.subscription_tier in [SubscriptionTier.ADVANCED, SubscriptionTier.PRO, SubscriptionTier.UNLIMITED]:
            features.extend(["wav_output", "genre_optimization", "multiple_revisions"])

        if self.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.UNLIMITED]:
            features.extend(["stem_mastering", "reference_matching", "flac_output", "unlimited_revisions"])

        if self.subscription_tier == SubscriptionTier.UNLIMITED:
            features.extend(["priority_processing", "unlimited_tracks"])

        return features
