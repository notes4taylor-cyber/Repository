"""
Motion-based target detection.
Detects moving objects by comparing consecutive frames.
Works when color detection fails due to inconsistent colors.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional
from collections import deque


@dataclass
class MovingTarget:
    """Represents a detected moving target."""
    x: int  # Center X in capture region
    y: int  # Center Y in capture region
    width: int
    height: int
    area: int
    motion_intensity: float  # How much movement detected
    distance_from_center: float


class MotionDetector:
    def __init__(
        self,
        min_area: int = 100,
        max_area: int = 50000,
        motion_threshold: int = 25,
        blur_kernel: int = 5,
        history_frames: int = 3,
    ):
        """
        Initialize motion detector.

        Args:
            min_area: Minimum contour area to consider as target
            max_area: Maximum contour area to consider as target
            motion_threshold: Pixel difference threshold to count as motion (0-255)
            blur_kernel: Gaussian blur kernel size for noise reduction
            history_frames: Number of frames to keep for motion comparison
        """
        self.min_area = min_area
        self.max_area = max_area
        self.motion_threshold = motion_threshold
        self.blur_kernel = blur_kernel
        self.history_frames = history_frames

        # Frame history for motion detection
        self._frame_history: deque = deque(maxlen=history_frames)
        self._background = None
        self._frame_count = 0

    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Convert to grayscale and blur."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.blur_kernel > 1:
            gray = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
        return gray

    def detect(self, frame: np.ndarray) -> list[MovingTarget]:
        """
        Detect moving targets in the frame.

        Args:
            frame: BGR image as numpy array

        Returns:
            List of detected moving targets, sorted by distance from center
        """
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Preprocess current frame
        gray = self._preprocess_frame(frame)

        # Need at least one previous frame
        if len(self._frame_history) == 0:
            self._frame_history.append(gray)
            return []

        # Compare with previous frame(s)
        # Use frame differencing
        prev_frame = self._frame_history[-1]

        # Calculate absolute difference
        frame_diff = cv2.absdiff(gray, prev_frame)

        # If we have more history, accumulate differences
        if len(self._frame_history) >= 2:
            for i in range(len(self._frame_history) - 1):
                diff = cv2.absdiff(self._frame_history[i], self._frame_history[i + 1])
                frame_diff = cv2.add(frame_diff, diff)

        # Add current frame to history
        self._frame_history.append(gray)

        # Threshold the difference
        _, motion_mask = cv2.threshold(frame_diff, self.motion_threshold, 255, cv2.THRESH_BINARY)

        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel)
        motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel)

        # Dilate to connect nearby motion areas
        motion_mask = cv2.dilate(motion_mask, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(motion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        targets = []
        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Filter out very wide or very tall shapes (likely not players)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 4 or aspect_ratio < 0.2:
                continue

            # Calculate center of target
            target_center_x = x + w // 2
            target_center_y = y + h // 2

            # Calculate motion intensity (average pixel difference in this region)
            roi = frame_diff[y:y+h, x:x+w]
            motion_intensity = np.mean(roi) if roi.size > 0 else 0

            # Calculate distance from crosshair
            distance = np.sqrt((target_center_x - center_x) ** 2 + (target_center_y - center_y) ** 2)

            targets.append(MovingTarget(
                x=target_center_x,
                y=target_center_y,
                width=w,
                height=h,
                area=area,
                motion_intensity=motion_intensity,
                distance_from_center=distance,
            ))

        # Sort by distance from center (closest first)
        targets.sort(key=lambda t: t.distance_from_center)

        return targets

    def detect_closest(self, frame: np.ndarray) -> Optional[MovingTarget]:
        """
        Detect and return only the closest moving target to center.

        Args:
            frame: BGR image as numpy array

        Returns:
            Closest moving target or None if no targets found
        """
        targets = self.detect(frame)
        return targets[0] if targets else None

    def get_debug_frame(self, frame: np.ndarray, targets: list[MovingTarget]) -> np.ndarray:
        """
        Create a debug visualization of detections.

        Args:
            frame: Original BGR frame
            targets: List of detected targets

        Returns:
            Frame with detection visualizations drawn
        """
        debug_frame = frame.copy()
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Draw crosshair at center
        cv2.line(debug_frame, (center_x - 10, center_y), (center_x + 10, center_y), (0, 255, 0), 1)
        cv2.line(debug_frame, (center_x, center_y - 10), (center_x, center_y + 10), (0, 255, 0), 1)

        # Draw detected targets
        for i, target in enumerate(targets):
            color = (0, 0, 255) if i == 0 else (255, 0, 0)  # Red for closest, blue for others

            # Draw bounding box
            x1 = target.x - target.width // 2
            y1 = target.y - target.height // 2
            x2 = target.x + target.width // 2
            y2 = target.y + target.height // 2
            cv2.rectangle(debug_frame, (x1, y1), (x2, y2), color, 2)

            # Draw center point
            cv2.circle(debug_frame, (target.x, target.y), 3, color, -1)

            # Draw line from center to target
            if i == 0:
                cv2.line(debug_frame, (center_x, center_y), (target.x, target.y), (0, 255, 255), 1)

            # Show motion intensity
            cv2.putText(debug_frame, f"{target.motion_intensity:.0f}", (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        return debug_frame

    def reset(self):
        """Clear frame history (call when restarting detection)."""
        self._frame_history.clear()
        self._background = None
