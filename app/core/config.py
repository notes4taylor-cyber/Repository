"""
MasterFlow Configuration
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "MasterFlow"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-Powered Music Mastering - Better Quality, Better Prices"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./masterflow.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-masterflow-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # File Upload
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_AUDIO_EXTENSIONS: set = {".wav", ".mp3", ".flac", ".aiff", ".ogg", ".m4a"}

    # Audio Processing
    DEFAULT_SAMPLE_RATE: int = 44100
    HIGH_QUALITY_SAMPLE_RATE: int = 96000
    DEFAULT_BIT_DEPTH: int = 24

    # Pricing (in cents) - CHEAPER THAN LANDR!
    PRICING: dict = {
        "basic": {
            "name": "Basic Master",
            "price": 499,  # $4.99
            "description": "Perfect for demos and personal projects",
            "features": ["AI mastering", "MP3 output", "1 revision"]
        },
        "advanced": {
            "name": "Advanced Master",
            "price": 799,  # $7.99
            "description": "Professional quality for releases",
            "features": ["AI mastering", "WAV + MP3 output", "3 revisions", "Genre optimization"]
        },
        "pro": {
            "name": "Pro Master",
            "price": 1299,  # $12.99
            "description": "Studio-grade mastering",
            "features": ["AI mastering", "All formats", "Unlimited revisions", "Stem mastering", "Reference matching"]
        },
        "unlimited_monthly": {
            "name": "Unlimited Monthly",
            "price": 1499,  # $14.99/month
            "description": "Unlimited masters per month",
            "features": ["Everything in Pro", "Unlimited tracks", "Priority processing"]
        },
        "unlimited_yearly": {
            "name": "Unlimited Yearly",
            "price": 9900,  # $99/year (vs LANDR's $199!)
            "description": "Best value - unlimited for a year",
            "features": ["Everything in Pro", "Unlimited tracks", "Priority processing", "2 months free"]
        }
    }

    # Mastering Presets
    MASTERING_PRESETS: dict = {
        "balanced": {
            "name": "Balanced",
            "description": "Neutral, transparent mastering",
            "eq_low_gain": 0.0,
            "eq_mid_gain": 0.0,
            "eq_high_gain": 0.0,
            "compression_ratio": 2.5,
            "compression_threshold": -18,
            "limiter_ceiling": -0.3,
            "target_lufs": -14
        },
        "warm": {
            "name": "Warm",
            "description": "Rich lows, smooth highs",
            "eq_low_gain": 2.0,
            "eq_mid_gain": 0.5,
            "eq_high_gain": -1.0,
            "compression_ratio": 3.0,
            "compression_threshold": -16,
            "limiter_ceiling": -0.3,
            "target_lufs": -14
        },
        "bright": {
            "name": "Bright",
            "description": "Crisp highs, clear presence",
            "eq_low_gain": -0.5,
            "eq_mid_gain": 1.0,
            "eq_high_gain": 2.5,
            "compression_ratio": 2.0,
            "compression_threshold": -20,
            "limiter_ceiling": -0.3,
            "target_lufs": -14
        },
        "punchy": {
            "name": "Punchy",
            "description": "Aggressive, impactful sound",
            "eq_low_gain": 1.5,
            "eq_mid_gain": 2.0,
            "eq_high_gain": 1.0,
            "compression_ratio": 4.0,
            "compression_threshold": -14,
            "limiter_ceiling": -0.1,
            "target_lufs": -11
        },
        "gentle": {
            "name": "Gentle",
            "description": "Subtle enhancement, dynamic range preserved",
            "eq_low_gain": 0.5,
            "eq_mid_gain": 0.0,
            "eq_high_gain": 0.5,
            "compression_ratio": 1.5,
            "compression_threshold": -24,
            "limiter_ceiling": -1.0,
            "target_lufs": -16
        }
    }

    # Genre Presets
    GENRE_PRESETS: dict = {
        "edm": {"target_lufs": -8, "compression_ratio": 4.5, "eq_low_gain": 3.0},
        "hiphop": {"target_lufs": -10, "compression_ratio": 4.0, "eq_low_gain": 2.5},
        "rock": {"target_lufs": -12, "compression_ratio": 3.5, "eq_mid_gain": 1.5},
        "pop": {"target_lufs": -14, "compression_ratio": 3.0, "eq_high_gain": 1.0},
        "jazz": {"target_lufs": -18, "compression_ratio": 2.0, "eq_mid_gain": 0.5},
        "classical": {"target_lufs": -20, "compression_ratio": 1.5, "eq_high_gain": 0.5},
        "rnb": {"target_lufs": -12, "compression_ratio": 3.0, "eq_low_gain": 2.0},
        "metal": {"target_lufs": -10, "compression_ratio": 5.0, "eq_mid_gain": 2.0},
        "acoustic": {"target_lufs": -16, "compression_ratio": 2.0, "eq_high_gain": 1.5},
        "electronic": {"target_lufs": -9, "compression_ratio": 4.0, "eq_low_gain": 2.5}
    }

    class Config:
        env_file = ".env"


settings = Settings()

# Create directories if they don't exist
settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.OUTPUT_DIR.mkdir(exist_ok=True)
