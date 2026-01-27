"""
Audio Analysis Module

Analyzes audio files to determine optimal mastering parameters.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
import warnings

warnings.filterwarnings("ignore")


@dataclass
class AudioAnalysis:
    """Results of audio analysis."""

    # Loudness
    peak_db: float
    rms_db: float
    lufs: float
    dynamic_range: float

    # Frequency
    low_energy: float  # 20-250 Hz
    mid_energy: float  # 250-4000 Hz
    high_energy: float  # 4000-20000 Hz
    spectral_centroid: float
    spectral_balance: str  # "bass-heavy", "balanced", "bright"

    # Stereo
    stereo_width: float
    correlation: float  # -1 to 1, mono compatibility
    balance: float  # -1 (left) to 1 (right)

    # Dynamics
    crest_factor: float
    transient_density: float

    # Recommendations
    recommended_preset: str
    recommended_target_lufs: float
    needs_eq_correction: bool
    eq_suggestions: dict


class AudioAnalyzer:
    """Analyzes audio to determine optimal mastering settings."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def analyze(self, audio: np.ndarray) -> AudioAnalysis:
        """
        Perform comprehensive audio analysis.

        Args:
            audio: Audio data as numpy array (samples x channels)

        Returns:
            AudioAnalysis object with all metrics
        """
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])

        # Get mono mix for some analyses
        mono = np.mean(audio, axis=1)

        # Loudness analysis
        peak_db = self._calculate_peak_db(audio)
        rms_db = self._calculate_rms_db(audio)
        lufs = self._calculate_lufs(audio)
        dynamic_range = peak_db - rms_db

        # Frequency analysis
        low_energy, mid_energy, high_energy = self._analyze_frequency_bands(mono)
        spectral_centroid = self._calculate_spectral_centroid(mono)
        spectral_balance = self._determine_spectral_balance(low_energy, mid_energy, high_energy)

        # Stereo analysis
        stereo_width = self._calculate_stereo_width(audio)
        correlation = self._calculate_correlation(audio)
        balance = self._calculate_balance(audio)

        # Dynamics analysis
        crest_factor = self._calculate_crest_factor(mono)
        transient_density = self._analyze_transients(mono)

        # Generate recommendations
        recommended_preset = self._recommend_preset(
            spectral_balance, dynamic_range, crest_factor
        )
        recommended_target_lufs = self._recommend_target_lufs(
            dynamic_range, crest_factor
        )
        needs_eq_correction, eq_suggestions = self._suggest_eq(
            low_energy, mid_energy, high_energy
        )

        return AudioAnalysis(
            peak_db=peak_db,
            rms_db=rms_db,
            lufs=lufs,
            dynamic_range=dynamic_range,
            low_energy=low_energy,
            mid_energy=mid_energy,
            high_energy=high_energy,
            spectral_centroid=spectral_centroid,
            spectral_balance=spectral_balance,
            stereo_width=stereo_width,
            correlation=correlation,
            balance=balance,
            crest_factor=crest_factor,
            transient_density=transient_density,
            recommended_preset=recommended_preset,
            recommended_target_lufs=recommended_target_lufs,
            needs_eq_correction=needs_eq_correction,
            eq_suggestions=eq_suggestions,
        )

    def _calculate_peak_db(self, audio: np.ndarray) -> float:
        """Calculate peak level in dB."""
        peak = np.max(np.abs(audio))
        if peak == 0:
            return -100.0
        return 20 * np.log10(peak)

    def _calculate_rms_db(self, audio: np.ndarray) -> float:
        """Calculate RMS level in dB."""
        rms = np.sqrt(np.mean(audio**2))
        if rms == 0:
            return -100.0
        return 20 * np.log10(rms)

    def _calculate_lufs(self, audio: np.ndarray) -> float:
        """
        Calculate integrated loudness (simplified LUFS).

        Note: This is a simplified implementation. For broadcast-compliant
        LUFS, consider using the pyloudnorm library.
        """
        # K-weighting filter coefficients (simplified)
        # Apply high-shelf boost at 1500 Hz and high-pass at 60 Hz

        # For now, use RMS-based approximation
        rms = np.sqrt(np.mean(audio**2))
        if rms == 0:
            return -100.0

        # Approximate LUFS (typically ~3dB lower than RMS for most content)
        lufs_approx = 20 * np.log10(rms) - 3.0
        return lufs_approx

    def _analyze_frequency_bands(
        self, mono: np.ndarray
    ) -> Tuple[float, float, float]:
        """Analyze energy in low, mid, and high frequency bands."""
        # Apply FFT
        n = len(mono)
        fft = np.fft.rfft(mono)
        freqs = np.fft.rfftfreq(n, 1 / self.sample_rate)
        magnitudes = np.abs(fft)

        # Define band boundaries
        low_mask = freqs < 250
        mid_mask = (freqs >= 250) & (freqs < 4000)
        high_mask = freqs >= 4000

        # Calculate energy in each band
        total_energy = np.sum(magnitudes**2)
        if total_energy == 0:
            return 0.33, 0.33, 0.34

        low_energy = np.sum(magnitudes[low_mask] ** 2) / total_energy
        mid_energy = np.sum(magnitudes[mid_mask] ** 2) / total_energy
        high_energy = np.sum(magnitudes[high_mask] ** 2) / total_energy

        return low_energy, mid_energy, high_energy

    def _calculate_spectral_centroid(self, mono: np.ndarray) -> float:
        """Calculate spectral centroid (brightness indicator)."""
        n = len(mono)
        fft = np.fft.rfft(mono)
        freqs = np.fft.rfftfreq(n, 1 / self.sample_rate)
        magnitudes = np.abs(fft)

        total_magnitude = np.sum(magnitudes)
        if total_magnitude == 0:
            return 0.0

        centroid = np.sum(freqs * magnitudes) / total_magnitude
        return centroid

    def _determine_spectral_balance(
        self, low: float, mid: float, high: float
    ) -> str:
        """Determine overall spectral balance."""
        if low > mid * 1.5 and low > high * 2:
            return "bass-heavy"
        elif high > mid * 0.8 and high > low * 1.5:
            return "bright"
        else:
            return "balanced"

    def _calculate_stereo_width(self, audio: np.ndarray) -> float:
        """Calculate stereo width (0 = mono, 1 = wide stereo)."""
        if audio.shape[1] < 2:
            return 0.0

        left = audio[:, 0]
        right = audio[:, 1]

        mid = (left + right) / 2
        side = (left - right) / 2

        mid_energy = np.sum(mid**2)
        side_energy = np.sum(side**2)

        if mid_energy == 0:
            return 1.0

        width = side_energy / (mid_energy + side_energy)
        return width

    def _calculate_correlation(self, audio: np.ndarray) -> float:
        """Calculate stereo correlation (-1 to 1)."""
        if audio.shape[1] < 2:
            return 1.0

        left = audio[:, 0]
        right = audio[:, 1]

        correlation = np.corrcoef(left, right)[0, 1]
        return correlation if not np.isnan(correlation) else 1.0

    def _calculate_balance(self, audio: np.ndarray) -> float:
        """Calculate stereo balance (-1 = left, 1 = right)."""
        if audio.shape[1] < 2:
            return 0.0

        left_energy = np.sum(audio[:, 0] ** 2)
        right_energy = np.sum(audio[:, 1] ** 2)

        total = left_energy + right_energy
        if total == 0:
            return 0.0

        return (right_energy - left_energy) / total

    def _calculate_crest_factor(self, mono: np.ndarray) -> float:
        """Calculate crest factor (peak to RMS ratio in dB)."""
        peak = np.max(np.abs(mono))
        rms = np.sqrt(np.mean(mono**2))

        if rms == 0:
            return 0.0

        return 20 * np.log10(peak / rms)

    def _analyze_transients(self, mono: np.ndarray) -> float:
        """Analyze transient density (0 to 1)."""
        # Calculate envelope using RMS windows
        window_size = int(self.sample_rate * 0.01)  # 10ms windows
        hop_size = window_size // 2

        envelope = []
        for i in range(0, len(mono) - window_size, hop_size):
            window = mono[i : i + window_size]
            envelope.append(np.sqrt(np.mean(window**2)))

        envelope = np.array(envelope)
        if len(envelope) < 2:
            return 0.5

        # Calculate derivative to find transients
        diff = np.diff(envelope)
        threshold = np.std(diff) * 2

        transient_count = np.sum(diff > threshold)
        duration_seconds = len(mono) / self.sample_rate

        # Normalize to 0-1 range (assuming typical range of 0-10 transients per second)
        density = min(1.0, (transient_count / duration_seconds) / 10)
        return density

    def _recommend_preset(
        self, spectral_balance: str, dynamic_range: float, crest_factor: float
    ) -> str:
        """Recommend a mastering preset based on analysis."""
        if spectral_balance == "bass-heavy":
            return "bright"  # Add high-end clarity
        elif spectral_balance == "bright":
            return "warm"  # Add warmth
        elif dynamic_range < 8:
            return "gentle"  # Already compressed, be subtle
        elif crest_factor > 15:
            return "punchy"  # Lots of dynamics, can push harder
        else:
            return "balanced"

    def _recommend_target_lufs(
        self, dynamic_range: float, crest_factor: float
    ) -> float:
        """Recommend target LUFS based on content."""
        # More dynamic content should stay quieter
        if crest_factor > 18:
            return -16.0  # Very dynamic, preserve it
        elif crest_factor > 14:
            return -14.0  # Standard streaming target
        elif crest_factor > 10:
            return -12.0  # Moderate compression OK
        else:
            return -11.0  # Already dense, can push it

    def _suggest_eq(
        self, low: float, mid: float, high: float
    ) -> Tuple[bool, dict]:
        """Suggest EQ corrections."""
        suggestions = {}
        needs_correction = False

        # Check for imbalances
        if low > 0.5:
            suggestions["low"] = -2.0  # Cut bass
            needs_correction = True
        elif low < 0.15:
            suggestions["low"] = 2.0  # Boost bass
            needs_correction = True

        if high > 0.35:
            suggestions["high"] = -1.5  # Cut highs
            needs_correction = True
        elif high < 0.1:
            suggestions["high"] = 2.0  # Boost highs
            needs_correction = True

        return needs_correction, suggestions
