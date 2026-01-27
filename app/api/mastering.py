"""
Mastering API endpoints.
"""
import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import get_db
from app.models.track import Track, MasteringJob, JobStatus
from app.models.user import User
from app.core.security import get_current_user_id
from app.core.config import settings
from app.services.mastering import MasteringEngine
from app.services.mastering.engine import MasteringSettings

router = APIRouter()


class MasteringRequest(BaseModel):
    """Schema for mastering request."""
    track_id: int
    preset: str = "balanced"  # balanced, warm, bright, punchy, gentle
    genre: Optional[str] = None  # edm, hiphop, rock, pop, jazz, classical, etc.
    target_lufs: float = -14.0
    output_format: str = "wav"  # wav, flac, mp3

    # Advanced settings (optional)
    eq_low_gain: Optional[float] = None
    eq_mid_gain: Optional[float] = None
    eq_high_gain: Optional[float] = None
    stereo_width: Optional[float] = None
    exciter_amount: Optional[float] = None


class MasteringJobResponse(BaseModel):
    """Schema for mastering job response."""
    id: int
    track_id: int
    status: str
    progress: float
    preset: str
    genre: Optional[str]
    target_lufs: float
    output_format: str
    input_lufs: Optional[float]
    output_lufs: Optional[float]
    gain_applied: Optional[float]
    processing_time: Optional[float]
    created_at: str
    completed_at: Optional[str]
    error_message: Optional[str]


class PresetInfo(BaseModel):
    """Schema for preset information."""
    name: str
    description: str
    eq_low_gain: float
    eq_mid_gain: float
    eq_high_gain: float
    compression_ratio: float
    target_lufs: float


@router.post("/master", response_model=MasteringJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_mastering(
    request: MasteringRequest,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a mastering job for a track.

    The mastering process runs in the background. Use the job status endpoint
    to check progress and get the download link when complete.
    """
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user can master
    if not user.can_master:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits. Please purchase credits or subscribe to continue."
        )

    # Get track
    result = await db.execute(
        select(Track).where(Track.id == request.track_id, Track.user_id == user_id)
    )
    track = result.scalar_one_or_none()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Validate preset
    if request.preset not in settings.MASTERING_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid preset. Available: {', '.join(settings.MASTERING_PRESETS.keys())}"
        )

    # Validate genre if provided
    if request.genre and request.genre not in settings.GENRE_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid genre. Available: {', '.join(settings.GENRE_PRESETS.keys())}"
        )

    # Build settings dict
    job_settings = {
        "preset": request.preset,
        "genre": request.genre,
        "target_lufs": request.target_lufs,
        "output_format": request.output_format,
    }

    # Add advanced settings if provided
    if request.eq_low_gain is not None:
        job_settings["eq_low_gain"] = request.eq_low_gain
    if request.eq_mid_gain is not None:
        job_settings["eq_mid_gain"] = request.eq_mid_gain
    if request.eq_high_gain is not None:
        job_settings["eq_high_gain"] = request.eq_high_gain
    if request.stereo_width is not None:
        job_settings["stereo_width"] = request.stereo_width
    if request.exciter_amount is not None:
        job_settings["exciter_amount"] = request.exciter_amount

    # Create mastering job
    job = MasteringJob(
        user_id=user_id,
        track_id=track.id,
        status=JobStatus.PENDING.value,
        settings=job_settings,
        preset=request.preset,
        genre=request.genre,
        target_lufs=request.target_lufs,
        output_format=request.output_format,
        price_cents=settings.PRICING["basic"]["price"],  # Default to basic pricing
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Start background processing
    background_tasks.add_task(process_mastering_job, job.id)

    return MasteringJobResponse(
        id=job.id,
        track_id=job.track_id,
        status=job.status,
        progress=job.progress,
        preset=job.preset,
        genre=job.genre,
        target_lufs=job.target_lufs,
        output_format=job.output_format,
        input_lufs=job.input_lufs,
        output_lufs=job.output_lufs,
        gain_applied=job.gain_applied,
        processing_time=job.processing_time,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error_message=job.error_message,
    )


async def process_mastering_job(job_id: int):
    """
    Background task to process a mastering job.
    """
    from app.models.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Get job
            result = await db.execute(select(MasteringJob).where(MasteringJob.id == job_id))
            job = result.scalar_one_or_none()

            if not job:
                return

            # Get track
            result = await db.execute(select(Track).where(Track.id == job.track_id))
            track = result.scalar_one_or_none()

            if not track:
                job.status = JobStatus.FAILED.value
                job.error_message = "Track not found"
                await db.commit()
                return

            # Update status
            job.status = JobStatus.PROCESSING.value
            job.started_at = datetime.utcnow()
            job.progress = 10
            await db.commit()

            # Build mastering settings
            mastering_settings = MasteringSettings(
                preset=job.settings.get("preset", "balanced"),
                genre=job.settings.get("genre"),
                target_lufs=job.settings.get("target_lufs", -14.0),
                output_format=job.settings.get("output_format", "wav"),
            )

            # Apply any custom settings
            if "eq_low_gain" in job.settings:
                mastering_settings.eq_low_gain = job.settings["eq_low_gain"]
            if "eq_mid_gain" in job.settings:
                mastering_settings.eq_mid_gain = job.settings["eq_mid_gain"]
            if "eq_high_gain" in job.settings:
                mastering_settings.eq_high_gain = job.settings["eq_high_gain"]
            if "stereo_width" in job.settings:
                mastering_settings.stereo_width = job.settings["stereo_width"]
            if "exciter_amount" in job.settings:
                mastering_settings.exciter_amount = job.settings["exciter_amount"]

            # Process
            job.progress = 20
            await db.commit()

            engine = MasteringEngine()
            result = engine.master(
                input_path=track.file_path,
                mastering_settings=mastering_settings,
            )

            job.progress = 90
            await db.commit()

            if result.success:
                job.status = JobStatus.COMPLETED.value
                job.output_path = result.output_path
                job.preview_path = result.preview_path
                job.input_lufs = result.input_analysis.lufs if result.input_analysis else None
                job.output_lufs = result.output_analysis.lufs if result.output_analysis else None
                job.gain_applied = result.gain_applied
                job.processing_time = result.duration_seconds

                # Store analysis
                if result.input_analysis:
                    job.input_analysis = {
                        "lufs": result.input_analysis.lufs,
                        "peak_db": result.input_analysis.peak_db,
                        "dynamic_range": result.input_analysis.dynamic_range,
                    }
                if result.output_analysis:
                    job.output_analysis = {
                        "lufs": result.output_analysis.lufs,
                        "peak_db": result.output_analysis.peak_db,
                        "dynamic_range": result.output_analysis.dynamic_range,
                    }

                # Update user stats
                user_result = await db.execute(select(User).where(User.id == job.user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    user.tracks_mastered += 1
                    user.total_processing_time += result.duration_seconds
                    if user.credits > 0:
                        user.credits -= 1  # Deduct credit

            else:
                job.status = JobStatus.FAILED.value
                job.error_message = result.error_message

            job.progress = 100
            job.completed_at = datetime.utcnow()
            await db.commit()

        except Exception as e:
            job.status = JobStatus.FAILED.value
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            await db.commit()


@router.get("/jobs", response_model=List[MasteringJobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all mastering jobs for the current user.
    """
    query = select(MasteringJob).where(MasteringJob.user_id == user_id)

    if status_filter:
        query = query.where(MasteringJob.status == status_filter)

    query = query.order_by(MasteringJob.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return [
        MasteringJobResponse(
            id=j.id,
            track_id=j.track_id,
            status=j.status,
            progress=j.progress,
            preset=j.preset,
            genre=j.genre,
            target_lufs=j.target_lufs,
            output_format=j.output_format,
            input_lufs=j.input_lufs,
            output_lufs=j.output_lufs,
            gain_applied=j.gain_applied,
            processing_time=j.processing_time,
            created_at=j.created_at.isoformat(),
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
            error_message=j.error_message,
        )
        for j in jobs
    ]


@router.get("/jobs/{job_id}", response_model=MasteringJobResponse)
async def get_job(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of a specific mastering job.
    """
    result = await db.execute(
        select(MasteringJob).where(
            MasteringJob.id == job_id,
            MasteringJob.user_id == user_id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return MasteringJobResponse(
        id=job.id,
        track_id=job.track_id,
        status=job.status,
        progress=job.progress,
        preset=job.preset,
        genre=job.genre,
        target_lufs=job.target_lufs,
        output_format=job.output_format,
        input_lufs=job.input_lufs,
        output_lufs=job.output_lufs,
        gain_applied=job.gain_applied,
        processing_time=job.processing_time,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        error_message=job.error_message,
    )


@router.get("/jobs/{job_id}/download")
async def download_mastered_track(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Download the mastered track.
    """
    result = await db.execute(
        select(MasteringJob).where(
            MasteringJob.id == job_id,
            MasteringJob.user_id == user_id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Job not completed yet")

    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    # Get original track name
    track_result = await db.execute(select(Track).where(Track.id == job.track_id))
    track = track_result.scalar_one_or_none()

    filename = f"{track.title or 'track'}_mastered.{job.output_format}"

    return FileResponse(
        job.output_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@router.get("/jobs/{job_id}/preview")
async def download_preview(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a 30-second preview of the mastered track.
    """
    result = await db.execute(
        select(MasteringJob).where(
            MasteringJob.id == job_id,
            MasteringJob.user_id == user_id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.preview_path or not os.path.exists(job.preview_path):
        raise HTTPException(status_code=404, detail="Preview not available")

    return FileResponse(
        job.preview_path,
        filename="preview.wav",
        media_type="audio/wav"
    )


@router.get("/presets", response_model=dict)
async def list_presets():
    """
    List all available mastering presets.
    """
    return {
        "presets": settings.MASTERING_PRESETS,
        "genres": list(settings.GENRE_PRESETS.keys()),
    }


@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending or processing job.
    """
    result = await db.execute(
        select(MasteringJob).where(
            MasteringJob.id == job_id,
            MasteringJob.user_id == user_id
        )
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in [JobStatus.COMPLETED.value, JobStatus.CANCELLED.value]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or already cancelled job")

    job.status = JobStatus.CANCELLED.value
    await db.commit()

    return {"message": "Job cancelled successfully"}
