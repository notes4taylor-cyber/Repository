"""
Track upload and management API endpoints.
"""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import soundfile as sf

from app.models.database import get_db
from app.models.track import Track
from app.models.user import User
from app.core.security import get_current_user_id
from app.core.config import settings

router = APIRouter()


class TrackResponse(BaseModel):
    """Schema for track response."""
    id: int
    original_filename: str
    title: Optional[str]
    artist: Optional[str]
    genre: Optional[str]
    duration: Optional[float]
    sample_rate: Optional[int]
    channels: Optional[int]
    file_size: Optional[int]
    uploaded_at: str
    analysis: Optional[dict]

    class Config:
        from_attributes = True


class TrackUpdate(BaseModel):
    """Schema for updating track metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None


@router.post("/upload", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def upload_track(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    artist: Optional[str] = None,
    genre: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an audio file for mastering.

    Supported formats: WAV, MP3, FLAC, AIFF, OGG, M4A
    Maximum file size: 500MB
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = settings.UPLOAD_DIR / unique_filename

    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()

            # Check file size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB"
                )

            await f.write(content)

        # Get audio info
        try:
            info = sf.info(str(file_path))
            duration = info.duration
            sample_rate = info.samplerate
            channels = info.channels
        except Exception:
            duration = None
            sample_rate = None
            channels = None

        # Create track record
        track = Track(
            user_id=user_id,
            original_filename=file.filename,
            stored_filename=unique_filename,
            file_path=str(file_path),
            file_size=len(content),
            title=title or Path(file.filename).stem,
            artist=artist,
            genre=genre,
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
        )

        db.add(track)
        await db.commit()
        await db.refresh(track)

        return TrackResponse(
            id=track.id,
            original_filename=track.original_filename,
            title=track.title,
            artist=track.artist,
            genre=track.genre,
            duration=track.duration,
            sample_rate=track.sample_rate,
            channels=track.channels,
            file_size=track.file_size,
            uploaded_at=track.uploaded_at.isoformat(),
            analysis=track.analysis,
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if something went wrong
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/", response_model=List[TrackResponse])
async def list_tracks(
    skip: int = 0,
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all tracks uploaded by the current user.
    """
    result = await db.execute(
        select(Track)
        .where(Track.user_id == user_id)
        .order_by(Track.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    tracks = result.scalars().all()

    return [
        TrackResponse(
            id=t.id,
            original_filename=t.original_filename,
            title=t.title,
            artist=t.artist,
            genre=t.genre,
            duration=t.duration,
            sample_rate=t.sample_rate,
            channels=t.channels,
            file_size=t.file_size,
            uploaded_at=t.uploaded_at.isoformat(),
            analysis=t.analysis,
        )
        for t in tracks
    ]


@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific track.
    """
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == user_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    return TrackResponse(
        id=track.id,
        original_filename=track.original_filename,
        title=track.title,
        artist=track.artist,
        genre=track.genre,
        duration=track.duration,
        sample_rate=track.sample_rate,
        channels=track.channels,
        file_size=track.file_size,
        uploaded_at=track.uploaded_at.isoformat(),
        analysis=track.analysis,
    )


@router.patch("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    update_data: TrackUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update track metadata.
    """
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == user_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if update_data.title is not None:
        track.title = update_data.title
    if update_data.artist is not None:
        track.artist = update_data.artist
    if update_data.album is not None:
        track.album = update_data.album
    if update_data.genre is not None:
        track.genre = update_data.genre

    await db.commit()
    await db.refresh(track)

    return TrackResponse(
        id=track.id,
        original_filename=track.original_filename,
        title=track.title,
        artist=track.artist,
        genre=track.genre,
        duration=track.duration,
        sample_rate=track.sample_rate,
        channels=track.channels,
        file_size=track.file_size,
        uploaded_at=track.uploaded_at.isoformat(),
        analysis=track.analysis,
    )


@router.delete("/{track_id}")
async def delete_track(
    track_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a track and its associated files.
    """
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == user_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Delete file
    if os.path.exists(track.file_path):
        os.remove(track.file_path)

    # Delete database record
    await db.delete(track)
    await db.commit()

    return {"message": "Track deleted successfully"}


@router.get("/{track_id}/download")
async def download_track(
    track_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Download the original uploaded track.
    """
    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == user_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    if not os.path.exists(track.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        track.file_path,
        filename=track.original_filename,
        media_type="application/octet-stream"
    )


@router.post("/{track_id}/analyze")
async def analyze_track(
    track_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a track to get recommendations for mastering settings.
    """
    from app.services.mastering import MasteringEngine

    result = await db.execute(
        select(Track).where(Track.id == track_id, Track.user_id == user_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        engine = MasteringEngine()
        analysis = engine.analyze_only(track.file_path)

        # Store analysis
        track.analysis = {
            "peak_db": analysis.peak_db,
            "rms_db": analysis.rms_db,
            "lufs": analysis.lufs,
            "dynamic_range": analysis.dynamic_range,
            "low_energy": analysis.low_energy,
            "mid_energy": analysis.mid_energy,
            "high_energy": analysis.high_energy,
            "spectral_balance": analysis.spectral_balance,
            "stereo_width": analysis.stereo_width,
            "correlation": analysis.correlation,
            "recommended_preset": analysis.recommended_preset,
            "recommended_target_lufs": analysis.recommended_target_lufs,
        }
        await db.commit()

        return {
            "track_id": track_id,
            "analysis": track.analysis,
            "recommendations": {
                "preset": analysis.recommended_preset,
                "target_lufs": analysis.recommended_target_lufs,
                "eq_suggestions": analysis.eq_suggestions,
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze track: {str(e)}"
        )
