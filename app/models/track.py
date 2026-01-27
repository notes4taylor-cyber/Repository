"""
Track and MasteringJob models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base


class JobStatus(enum.Enum):
    """Status of a mastering job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Track(Base):
    """Uploaded track model."""

    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File info
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)  # bytes

    # Audio metadata
    title = Column(String(500), nullable=True)
    artist = Column(String(255), nullable=True)
    album = Column(String(255), nullable=True)
    genre = Column(String(100), nullable=True)

    # Audio properties
    duration = Column(Float)  # seconds
    sample_rate = Column(Integer)
    bit_depth = Column(Integer)
    channels = Column(Integer)

    # Analysis results (stored as JSON)
    analysis = Column(JSON, nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tracks")
    mastering_jobs = relationship("MasteringJob", back_populates="track", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Track {self.title or self.original_filename}>"


class MasteringJob(Base):
    """Mastering job model."""

    __tablename__ = "mastering_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)

    # Status
    status = Column(String(50), default=JobStatus.PENDING.value)
    progress = Column(Float, default=0.0)  # 0-100

    # Mastering settings (stored as JSON)
    settings = Column(JSON, nullable=False)

    # Preset and genre
    preset = Column(String(50), default="balanced")
    genre = Column(String(50), nullable=True)

    # Target settings
    target_lufs = Column(Float, default=-14.0)
    output_format = Column(String(10), default="wav")

    # Output files
    output_path = Column(String(1000), nullable=True)
    preview_path = Column(String(1000), nullable=True)

    # Results
    input_lufs = Column(Float, nullable=True)
    output_lufs = Column(Float, nullable=True)
    gain_applied = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds

    # Analysis results
    input_analysis = Column(JSON, nullable=True)
    output_analysis = Column(JSON, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Billing
    price_cents = Column(Integer, nullable=True)
    paid = Column(Boolean, default=False)

    # Revision tracking
    revision_number = Column(Integer, default=1)
    parent_job_id = Column(Integer, ForeignKey("mastering_jobs.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="mastering_jobs")
    track = relationship("Track", back_populates="mastering_jobs")

    def __repr__(self):
        return f"<MasteringJob {self.id} - {self.status}>"

    def to_dict(self):
        """Convert job to dictionary for API response."""
        return {
            "id": self.id,
            "track_id": self.track_id,
            "status": self.status,
            "progress": self.progress,
            "preset": self.preset,
            "genre": self.genre,
            "target_lufs": self.target_lufs,
            "output_format": self.output_format,
            "input_lufs": self.input_lufs,
            "output_lufs": self.output_lufs,
            "gain_applied": self.gain_applied,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }
