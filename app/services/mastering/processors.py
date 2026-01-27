"""
Audio Processing Modules

Professional-grade audio processors for mastering.
"""
import numpy as np
from scipy import signal
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ProcessorSettings:
    """Base settings for processors."""

    bypass: bool = False


class Equalizer:
    """
    Parametric Equalizer with Low, Mid, and High bands.

    Uses biquad filters for smooth, musical EQ curves.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        low_gain: float = 0.0,
        mid_gain: float = 0.0,
        high_gain: float = 0.0,
        low_freq: float = 100.0,
        mid_freq: float = 1000.0,
        high_freq: float = 8000.0,
        q: float = 0.707,
    ) -> np.ndarray:
        """
        Apply parametric EQ to audio.

        Args:
            audio: Input audio (samples x channels)
            low_gain: Low band gain in dB (-12 to +12)
            mid_gain: Mid band gain in dB (-12 to +12)
            high_gain: High band gain in dB (-12 to +12)
            low_freq: Low band center frequency
            mid_freq: Mid band center frequency
            high_freq: High band center frequency
            q: Q factor (bandwidth)

        Returns:
            Processed audio
        """
        output = audio.copy()

        # Apply low shelf
        if abs(low_gain) > 0.1:
            output = self._apply_low_shelf(output, low_freq, low_gain)

        # Apply mid peak
        if abs(mid_gain) > 0.1:
            output = self._apply_peak(output, mid_freq, mid_gain, q)

        # Apply high shelf
        if abs(high_gain) > 0.1:
            output = self._apply_high_shelf(output, high_freq, high_gain)

        return output

    def _apply_low_shelf(
        self, audio: np.ndarray, freq: float, gain_db: float
    ) -> np.ndarray:
        """Apply low shelf filter."""
        A = 10 ** (gain_db / 40)
        w0 = 2 * np.pi * freq / self.sample_rate
        alpha = np.sin(w0) / 2 * np.sqrt(2)

        cos_w0 = np.cos(w0)

        b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
        b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
        a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
        a2 = (A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha

        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1 / a0, a2 / a0])

        return self._apply_filter(audio, b, a)

    def _apply_high_shelf(
        self, audio: np.ndarray, freq: float, gain_db: float
    ) -> np.ndarray:
        """Apply high shelf filter."""
        A = 10 ** (gain_db / 40)
        w0 = 2 * np.pi * freq / self.sample_rate
        alpha = np.sin(w0) / 2 * np.sqrt(2)

        cos_w0 = np.cos(w0)

        b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
        b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
        b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
        a0 = (A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
        a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
        a2 = (A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha

        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1 / a0, a2 / a0])

        return self._apply_filter(audio, b, a)

    def _apply_peak(
        self, audio: np.ndarray, freq: float, gain_db: float, q: float
    ) -> np.ndarray:
        """Apply peak/notch filter."""
        A = 10 ** (gain_db / 40)
        w0 = 2 * np.pi * freq / self.sample_rate
        alpha = np.sin(w0) / (2 * q)

        cos_w0 = np.cos(w0)

        b0 = 1 + alpha * A
        b1 = -2 * cos_w0
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * cos_w0
        a2 = 1 - alpha / A

        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1 / a0, a2 / a0])

        return self._apply_filter(audio, b, a)

    def _apply_filter(
        self, audio: np.ndarray, b: np.ndarray, a: np.ndarray
    ) -> np.ndarray:
        """Apply biquad filter to audio."""
        if audio.ndim == 1:
            return signal.lfilter(b, a, audio)
        else:
            output = np.zeros_like(audio)
            for ch in range(audio.shape[1]):
                output[:, ch] = signal.lfilter(b, a, audio[:, ch])
            return output


class Compressor:
    """
    Dynamic Range Compressor with soft-knee characteristic.

    Reduces dynamic range for a more consistent, polished sound.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        threshold: float = -18.0,
        ratio: float = 3.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
        knee_db: float = 6.0,
        makeup_gain: float = 0.0,
    ) -> np.ndarray:
        """
        Apply compression to audio.

        Args:
            audio: Input audio (samples x channels)
            threshold: Threshold in dB
            ratio: Compression ratio (e.g., 4.0 = 4:1)
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            knee_db: Soft knee width in dB
            makeup_gain: Output gain in dB

        Returns:
            Compressed audio
        """
        # Calculate time constants
        attack_coeff = np.exp(-1.0 / (self.sample_rate * attack_ms / 1000))
        release_coeff = np.exp(-1.0 / (self.sample_rate * release_ms / 1000))

        # Work with stereo
        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)

        # Calculate envelope (linked stereo)
        envelope_db = self._calculate_envelope(audio, attack_coeff, release_coeff)

        # Calculate gain reduction
        gain_reduction = self._calculate_gain_reduction(
            envelope_db, threshold, ratio, knee_db
        )

        # Apply gain reduction
        gain_linear = 10 ** ((gain_reduction + makeup_gain) / 20)
        output = audio * gain_linear.reshape(-1, 1)

        return output

    def _calculate_envelope(
        self, audio: np.ndarray, attack_coeff: float, release_coeff: float
    ) -> np.ndarray:
        """Calculate the envelope of the audio signal."""
        # Peak detection across channels
        peak = np.max(np.abs(audio), axis=1)

        # Convert to dB
        peak_db = np.where(peak > 1e-10, 20 * np.log10(peak), -100)

        # Smooth envelope
        envelope = np.zeros_like(peak_db)
        envelope[0] = peak_db[0]

        for i in range(1, len(peak_db)):
            if peak_db[i] > envelope[i - 1]:
                envelope[i] = attack_coeff * envelope[i - 1] + (1 - attack_coeff) * peak_db[i]
            else:
                envelope[i] = release_coeff * envelope[i - 1] + (1 - release_coeff) * peak_db[i]

        return envelope

    def _calculate_gain_reduction(
        self,
        envelope_db: np.ndarray,
        threshold: float,
        ratio: float,
        knee_db: float,
    ) -> np.ndarray:
        """Calculate gain reduction with soft knee."""
        gain_reduction = np.zeros_like(envelope_db)

        for i, level in enumerate(envelope_db):
            if level < threshold - knee_db / 2:
                # Below knee - no compression
                gain_reduction[i] = 0
            elif level > threshold + knee_db / 2:
                # Above knee - full compression
                gain_reduction[i] = (threshold - level) * (1 - 1 / ratio)
            else:
                # In knee - soft transition
                knee_factor = (level - threshold + knee_db / 2) / knee_db
                gain_reduction[i] = (
                    (1 / ratio - 1)
                    * (level - threshold + knee_db / 2) ** 2
                    / (2 * knee_db)
                )

        return gain_reduction


class Limiter:
    """
    Brickwall Limiter for final loudness maximization.

    Prevents clipping while maximizing perceived loudness.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        ceiling: float = -0.3,
        release_ms: float = 50.0,
        lookahead_ms: float = 5.0,
    ) -> np.ndarray:
        """
        Apply brickwall limiting to audio.

        Args:
            audio: Input audio (samples x channels)
            ceiling: Output ceiling in dB (e.g., -0.3 for streaming)
            release_ms: Release time in milliseconds
            lookahead_ms: Lookahead time in milliseconds

        Returns:
            Limited audio
        """
        ceiling_linear = 10 ** (ceiling / 20)
        lookahead_samples = int(self.sample_rate * lookahead_ms / 1000)
        release_coeff = np.exp(-1.0 / (self.sample_rate * release_ms / 1000))

        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)

        # Calculate required gain reduction
        peak = np.max(np.abs(audio), axis=1)
        gain_reduction = np.where(
            peak > ceiling_linear, ceiling_linear / (peak + 1e-10), 1.0
        )

        # Apply lookahead (find minimum gain in future samples)
        if lookahead_samples > 0:
            padded = np.pad(gain_reduction, (0, lookahead_samples), mode="edge")
            for i in range(len(gain_reduction)):
                gain_reduction[i] = np.min(padded[i : i + lookahead_samples + 1])

        # Smooth the gain reduction
        smoothed_gain = np.ones_like(gain_reduction)
        for i in range(1, len(gain_reduction)):
            if gain_reduction[i] < smoothed_gain[i - 1]:
                smoothed_gain[i] = gain_reduction[i]  # Instant attack
            else:
                smoothed_gain[i] = (
                    release_coeff * smoothed_gain[i - 1]
                    + (1 - release_coeff) * gain_reduction[i]
                )

        # Apply gain
        output = audio * smoothed_gain.reshape(-1, 1)

        return output


class StereoEnhancer:
    """
    Stereo Width Enhancement.

    Expands or narrows the stereo image.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        width: float = 1.0,
        bass_mono_freq: float = 120.0,
    ) -> np.ndarray:
        """
        Enhance stereo width.

        Args:
            audio: Input audio (samples x channels)
            width: Width factor (0 = mono, 1 = normal, 2 = extra wide)
            bass_mono_freq: Frequency below which to sum to mono

        Returns:
            Processed audio
        """
        if audio.ndim == 1 or audio.shape[1] < 2:
            return audio

        left = audio[:, 0]
        right = audio[:, 1]

        # Convert to mid/side
        mid = (left + right) / 2
        side = (left - right) / 2

        # Apply width
        side = side * width

        # Convert back to L/R
        new_left = mid + side
        new_right = mid - side

        # Mono the bass
        if bass_mono_freq > 0:
            # Create lowpass filter
            nyquist = self.sample_rate / 2
            normalized_freq = bass_mono_freq / nyquist
            b, a = signal.butter(2, normalized_freq, btype="low")

            # Extract bass
            bass_left = signal.lfilter(b, a, new_left)
            bass_right = signal.lfilter(b, a, new_right)
            bass_mono = (bass_left + bass_right) / 2

            # Create highpass for remaining signal
            b_hp, a_hp = signal.butter(2, normalized_freq, btype="high")
            high_left = signal.lfilter(b_hp, a_hp, new_left)
            high_right = signal.lfilter(b_hp, a_hp, new_right)

            # Combine
            new_left = bass_mono + high_left
            new_right = bass_mono + high_right

        return np.column_stack([new_left, new_right])


class HarmonicExciter:
    """
    Harmonic Exciter for adding presence and clarity.

    Generates subtle harmonics to enhance perceived brightness.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        drive: float = 0.3,
        mix: float = 0.15,
        high_freq: float = 3000.0,
    ) -> np.ndarray:
        """
        Add harmonic excitement to audio.

        Args:
            audio: Input audio (samples x channels)
            drive: Saturation drive amount (0-1)
            mix: Wet/dry mix for harmonics (0-1)
            high_freq: Frequency above which to apply exciter

        Returns:
            Processed audio
        """
        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)

        # Create highpass filter
        nyquist = self.sample_rate / 2
        normalized_freq = min(high_freq / nyquist, 0.99)
        b, a = signal.butter(2, normalized_freq, btype="high")

        output = np.zeros_like(audio)

        for ch in range(audio.shape[1]):
            # Extract high frequencies
            highs = signal.lfilter(b, a, audio[:, ch])

            # Apply soft saturation to generate harmonics
            saturated = np.tanh(highs * (1 + drive * 3)) / (1 + drive)

            # Mix harmonics back in
            output[:, ch] = audio[:, ch] + saturated * mix

        # Soft clip to prevent overs
        output = np.tanh(output)

        return output


class LoudnessNormalizer:
    """
    LUFS-based Loudness Normalization.

    Adjusts audio to meet target loudness standards.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        target_lufs: float = -14.0,
        max_gain: float = 12.0,
    ) -> Tuple[np.ndarray, float]:
        """
        Normalize audio to target LUFS.

        Args:
            audio: Input audio (samples x channels)
            target_lufs: Target loudness in LUFS
            max_gain: Maximum gain to apply in dB

        Returns:
            Tuple of (normalized audio, gain applied in dB)
        """
        # Calculate current loudness (simplified)
        rms = np.sqrt(np.mean(audio**2))
        if rms < 1e-10:
            return audio, 0.0

        current_lufs = 20 * np.log10(rms) - 3.0

        # Calculate required gain
        gain_db = target_lufs - current_lufs
        gain_db = np.clip(gain_db, -max_gain, max_gain)

        # Apply gain
        gain_linear = 10 ** (gain_db / 20)
        output = audio * gain_linear

        return output, gain_db
