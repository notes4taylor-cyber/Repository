"""
MasterFlow Mastering Engine

The core mastering engine that orchestrates all audio processing.
"""
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
import tempfile
import uuid

from app.services.mastering.analyzer import AudioAnalyzer, AudioAnalysis
from app.services.mastering.processors import (
    Equalizer,
    Compressor,
    Limiter,
    StereoEnhancer,
    HarmonicExciter,
    LoudnessNormalizer,
)
from app.core.config import settings


@dataclass
class MasteringSettings:
    """Settings for a mastering session."""

    # Preset (balanced, warm, bright, punchy, gentle)
    preset: str = "balanced"

    # Genre optimization
    genre: Optional[str] = None

    # Target loudness
    target_lufs: float = -14.0

    # EQ settings (dB)
    eq_low_gain: float = 0.0
    eq_mid_gain: float = 0.0
    eq_high_gain: float = 0.0

    # Compression
    compression_ratio: float = 2.5
    compression_threshold: float = -18.0

    # Limiter
    limiter_ceiling: float = -0.3

    # Stereo
    stereo_width: float = 1.0
    bass_mono: bool = True

    # Harmonic exciter
    exciter_amount: float = 0.0

    # Auto settings (use analysis to determine settings)
    auto_eq: bool = True
    auto_dynamics: bool = True

    # Output
    output_format: str = "wav"  # wav, flac, mp3
    output_sample_rate: int = 44100
    output_bit_depth: int = 24


@dataclass
class MasteringResult:
    """Result of a mastering operation."""

    success: bool
    output_path: Optional[str] = None
    preview_path: Optional[str] = None

    # Analysis
    input_analysis: Optional[AudioAnalysis] = None
    output_analysis: Optional[AudioAnalysis] = None

    # Processing info
    gain_applied: float = 0.0
    peak_reduction: float = 0.0

    # Metadata
    duration_seconds: float = 0.0
    sample_rate: int = 44100

    # Error info
    error_message: Optional[str] = None

    # Settings used
    settings_used: Dict[str, Any] = field(default_factory=dict)


class MasteringEngine:
    """
    Main mastering engine that processes audio files.

    This engine combines multiple processors in an optimized signal chain
    to produce professional-quality masters.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

        # Initialize processors
        self.analyzer = AudioAnalyzer(sample_rate)
        self.equalizer = Equalizer(sample_rate)
        self.compressor = Compressor(sample_rate)
        self.limiter = Limiter(sample_rate)
        self.stereo_enhancer = StereoEnhancer(sample_rate)
        self.exciter = HarmonicExciter(sample_rate)
        self.normalizer = LoudnessNormalizer(sample_rate)

    def master(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        mastering_settings: Optional[MasteringSettings] = None,
        generate_preview: bool = True,
    ) -> MasteringResult:
        """
        Master an audio file.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file (auto-generated if None)
            mastering_settings: Mastering settings (uses defaults if None)
            generate_preview: Whether to generate a 30-second preview

        Returns:
            MasteringResult with output paths and analysis
        """
        try:
            # Load settings
            if mastering_settings is None:
                mastering_settings = MasteringSettings()

            # Apply preset settings
            mastering_settings = self._apply_preset(mastering_settings)

            # Apply genre settings
            if mastering_settings.genre:
                mastering_settings = self._apply_genre(mastering_settings)

            # Load audio
            audio, file_sample_rate = sf.read(input_path, always_2d=True)

            # Resample if needed
            if file_sample_rate != self.sample_rate:
                audio = self._resample(audio, file_sample_rate, self.sample_rate)

            # Analyze input
            input_analysis = self.analyzer.analyze(audio)

            # Apply auto settings if enabled
            if mastering_settings.auto_eq and input_analysis.needs_eq_correction:
                mastering_settings = self._apply_auto_eq(
                    mastering_settings, input_analysis
                )

            if mastering_settings.auto_dynamics:
                mastering_settings = self._apply_auto_dynamics(
                    mastering_settings, input_analysis
                )

            # Process audio through the mastering chain
            processed = self._process_chain(audio, mastering_settings)

            # Analyze output
            output_analysis = self.analyzer.analyze(processed)

            # Calculate statistics
            input_peak = np.max(np.abs(audio))
            output_peak = np.max(np.abs(processed))
            peak_reduction = 20 * np.log10(input_peak / (output_peak + 1e-10))

            # Generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(
                    input_path, mastering_settings.output_format
                )

            # Save output
            self._save_audio(
                processed,
                output_path,
                mastering_settings.output_sample_rate,
                mastering_settings.output_bit_depth,
                mastering_settings.output_format,
            )

            # Generate preview if requested
            preview_path = None
            if generate_preview:
                preview_path = self._generate_preview(processed, output_path)

            # Calculate duration
            duration = len(audio) / self.sample_rate

            return MasteringResult(
                success=True,
                output_path=output_path,
                preview_path=preview_path,
                input_analysis=input_analysis,
                output_analysis=output_analysis,
                gain_applied=output_analysis.lufs - input_analysis.lufs,
                peak_reduction=peak_reduction,
                duration_seconds=duration,
                sample_rate=self.sample_rate,
                settings_used=self._settings_to_dict(mastering_settings),
            )

        except Exception as e:
            return MasteringResult(
                success=False,
                error_message=str(e),
            )

    def _apply_preset(self, settings: MasteringSettings) -> MasteringSettings:
        """Apply preset values to settings."""
        preset_config = settings_module.MASTERING_PRESETS.get(
            settings.preset, settings_module.MASTERING_PRESETS["balanced"]
        )

        # Only apply preset values if user hasn't customized them
        if settings.eq_low_gain == 0.0:
            settings.eq_low_gain = preset_config.get("eq_low_gain", 0.0)
        if settings.eq_mid_gain == 0.0:
            settings.eq_mid_gain = preset_config.get("eq_mid_gain", 0.0)
        if settings.eq_high_gain == 0.0:
            settings.eq_high_gain = preset_config.get("eq_high_gain", 0.0)
        if settings.compression_ratio == 2.5:
            settings.compression_ratio = preset_config.get("compression_ratio", 2.5)
        if settings.compression_threshold == -18.0:
            settings.compression_threshold = preset_config.get(
                "compression_threshold", -18.0
            )
        if settings.target_lufs == -14.0:
            settings.target_lufs = preset_config.get("target_lufs", -14.0)

        return settings

    def _apply_genre(self, settings: MasteringSettings) -> MasteringSettings:
        """Apply genre-specific settings."""
        genre_config = settings_module.GENRE_PRESETS.get(settings.genre, {})

        for key, value in genre_config.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        return settings

    def _apply_auto_eq(
        self, settings: MasteringSettings, analysis: AudioAnalysis
    ) -> MasteringSettings:
        """Apply automatic EQ based on analysis."""
        suggestions = analysis.eq_suggestions

        if "low" in suggestions:
            settings.eq_low_gain += suggestions["low"] * 0.5  # Apply 50% of suggestion
        if "high" in suggestions:
            settings.eq_high_gain += suggestions["high"] * 0.5

        return settings

    def _apply_auto_dynamics(
        self, settings: MasteringSettings, analysis: AudioAnalysis
    ) -> MasteringSettings:
        """Apply automatic dynamics settings based on analysis."""
        # Adjust target LUFS based on content
        settings.target_lufs = analysis.recommended_target_lufs

        # Adjust compression based on dynamic range
        if analysis.dynamic_range < 10:
            # Already compressed, use gentler settings
            settings.compression_ratio = min(settings.compression_ratio, 2.0)
            settings.compression_threshold = max(settings.compression_threshold, -20)
        elif analysis.dynamic_range > 18:
            # Very dynamic, can compress more
            settings.compression_ratio = max(settings.compression_ratio, 3.5)

        return settings

    def _process_chain(
        self, audio: np.ndarray, settings: MasteringSettings
    ) -> np.ndarray:
        """
        Process audio through the mastering chain.

        Signal flow:
        1. Input gain staging
        2. EQ
        3. Compression
        4. Stereo enhancement
        5. Harmonic exciter
        6. Loudness normalization
        7. Limiting
        """
        processed = audio.copy()

        # 1. Input gain staging - normalize to prevent clipping during processing
        peak = np.max(np.abs(processed))
        if peak > 0.9:
            processed = processed * (0.9 / peak)

        # 2. Equalization
        processed = self.equalizer.process(
            processed,
            low_gain=settings.eq_low_gain,
            mid_gain=settings.eq_mid_gain,
            high_gain=settings.eq_high_gain,
        )

        # 3. Compression
        processed = self.compressor.process(
            processed,
            threshold=settings.compression_threshold,
            ratio=settings.compression_ratio,
            attack_ms=15.0,
            release_ms=150.0,
        )

        # 4. Stereo enhancement
        if settings.stereo_width != 1.0 or settings.bass_mono:
            processed = self.stereo_enhancer.process(
                processed,
                width=settings.stereo_width,
                bass_mono_freq=120.0 if settings.bass_mono else 0.0,
            )

        # 5. Harmonic exciter
        if settings.exciter_amount > 0:
            processed = self.exciter.process(
                processed,
                drive=settings.exciter_amount * 0.5,
                mix=settings.exciter_amount * 0.2,
            )

        # 6. Loudness normalization
        processed, _ = self.normalizer.process(
            processed,
            target_lufs=settings.target_lufs,
        )

        # 7. Final limiting
        processed = self.limiter.process(
            processed,
            ceiling=settings.limiter_ceiling,
            release_ms=100.0,
        )

        return processed

    def _resample(
        self, audio: np.ndarray, orig_sr: int, target_sr: int
    ) -> np.ndarray:
        """Resample audio to target sample rate."""
        from scipy import signal

        if orig_sr == target_sr:
            return audio

        # Calculate resampling ratio
        ratio = target_sr / orig_sr
        new_length = int(len(audio) * ratio)

        if audio.ndim == 1:
            return signal.resample(audio, new_length)
        else:
            resampled = np.zeros((new_length, audio.shape[1]))
            for ch in range(audio.shape[1]):
                resampled[:, ch] = signal.resample(audio[:, ch], new_length)
            return resampled

    def _generate_output_path(self, input_path: str, output_format: str) -> str:
        """Generate output file path."""
        input_path = Path(input_path)
        output_dir = settings.OUTPUT_DIR
        output_name = f"{input_path.stem}_mastered_{uuid.uuid4().hex[:8]}.{output_format}"
        return str(output_dir / output_name)

    def _save_audio(
        self,
        audio: np.ndarray,
        output_path: str,
        sample_rate: int,
        bit_depth: int,
        output_format: str,
    ):
        """Save audio to file."""
        # Determine subtype based on format and bit depth
        if output_format == "wav":
            if bit_depth == 16:
                subtype = "PCM_16"
            elif bit_depth == 24:
                subtype = "PCM_24"
            else:
                subtype = "PCM_32"
        elif output_format == "flac":
            if bit_depth == 16:
                subtype = "PCM_16"
            else:
                subtype = "PCM_24"
        else:
            subtype = None

        sf.write(output_path, audio, sample_rate, subtype=subtype)

    def _generate_preview(self, audio: np.ndarray, output_path: str) -> str:
        """Generate a 30-second preview of the mastered audio."""
        preview_duration = 30  # seconds
        preview_samples = min(len(audio), self.sample_rate * preview_duration)

        # Take the first 30 seconds
        preview_audio = audio[:preview_samples]

        # Apply fade out at the end
        fade_samples = self.sample_rate * 2  # 2 second fade
        if len(preview_audio) > fade_samples:
            fade_curve = np.linspace(1, 0, fade_samples)
            if preview_audio.ndim == 2:
                fade_curve = fade_curve.reshape(-1, 1)
            preview_audio[-fade_samples:] *= fade_curve

        # Save preview
        preview_path = output_path.replace("_mastered_", "_preview_")
        preview_path = preview_path.rsplit(".", 1)[0] + ".mp3"

        # Save as WAV first (for compatibility), actual MP3 encoding would need additional library
        preview_path = preview_path.rsplit(".", 1)[0] + ".wav"
        sf.write(preview_path, preview_audio, self.sample_rate)

        return preview_path

    def _settings_to_dict(self, settings: MasteringSettings) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "preset": settings.preset,
            "genre": settings.genre,
            "target_lufs": settings.target_lufs,
            "eq_low_gain": settings.eq_low_gain,
            "eq_mid_gain": settings.eq_mid_gain,
            "eq_high_gain": settings.eq_high_gain,
            "compression_ratio": settings.compression_ratio,
            "compression_threshold": settings.compression_threshold,
            "limiter_ceiling": settings.limiter_ceiling,
            "stereo_width": settings.stereo_width,
            "output_format": settings.output_format,
        }

    def analyze_only(self, input_path: str) -> AudioAnalysis:
        """Analyze an audio file without processing."""
        audio, sample_rate = sf.read(input_path, always_2d=True)

        if sample_rate != self.sample_rate:
            audio = self._resample(audio, sample_rate, self.sample_rate)

        return self.analyzer.analyze(audio)


# Import settings at module level to avoid circular import
from app.core.config import settings as settings_module
