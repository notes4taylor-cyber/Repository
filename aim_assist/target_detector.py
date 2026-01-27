"""
Target detection module using color-based detection in HSV color space.
Detects targets based on configurable color ranges (e.g., enemy highlight colors).
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class Target:
    """Represents a detected target."""
    x: int  # Center X in capture region
    y: int  # Center Y in capture region
    width: int
    height: int
    area: int
    distance_from_center: float  # Distance from crosshair/center


@dataclass
class ColorRange:
    """HSV color range for detection."""
    lower: np.ndarray  # [H, S, V] lower bounds
    upper: np.ndarray  # [H, S, V] upper bounds
    name: str = "default"

    @classmethod
    def from_bgr(cls, bgr_color: tuple[int, int, int], tolerance: int = 30, name: str = "default") -> "ColorRange":
        """
        Create a color range from a BGR color with tolerance.

        Args:
            bgr_color: (B, G, R) color tuple
            tolerance: How much variance to allow in each HSV channel
            name: Name for this color range
        """
        # Convert BGR to HSV
        bgr_pixel = np.uint8([[list(bgr_color)]])
        hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)
        h, s, v = hsv_pixel[0][0]

        # Create range with tolerance
        # Hue wraps around at 180, so handle carefully
        h_tol = min(tolerance // 2, 20)
        s_tol = tolerance
        v_tol = tolerance

        lower = np.array([max(0, h - h_tol), max(0, s - s_tol), max(0, v - v_tol)])
        upper = np.array([min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol)])

        return cls(lower=lower, upper=upper, name=name)


# Common color presets for game targets
COLOR_PRESETS = {
    # Red tones (common enemy highlights)
    "red": ColorRange(
        lower=np.array([0, 100, 100]),
        upper=np.array([10, 255, 255]),
        name="red"
    ),
    "red_alt": ColorRange(
        lower=np.array([170, 100, 100]),
        upper=np.array([179, 255, 255]),
        name="red_alt"
    ),
    # Purple/magenta (some games use this)
    "purple": ColorRange(
        lower=np.array([140, 100, 100]),
        upper=np.array([160, 255, 255]),
        name="purple"
    ),
    # Yellow (common highlight color)
    "yellow": ColorRange(
        lower=np.array([20, 100, 100]),
        upper=np.array([35, 255, 255]),
        name="yellow"
    ),
    # Green
    "green": ColorRange(
        lower=np.array([40, 100, 100]),
        upper=np.array([80, 255, 255]),
        name="green"
    ),
    # Orange
    "orange": ColorRange(
        lower=np.array([10, 100, 100]),
        upper=np.array([20, 255, 255]),
        name="orange"
    ),
    # Cyan/light blue
    "cyan": ColorRange(
        lower=np.array([80, 100, 100]),
        upper=np.array([100, 255, 255]),
        name="cyan"
    ),
    # Bright white (for bright targets)
    "white": ColorRange(
        lower=np.array([0, 0, 200]),
        upper=np.array([179, 50, 255]),
        name="white"
    ),
}


class TargetDetector:
    def __init__(
        self,
        color_ranges: Optional[list[ColorRange]] = None,
        min_area: int = 50,
        max_area: int = 50000,
        blur_kernel: int = 3,
    ):
        """
        Initialize target detector.

        Args:
            color_ranges: List of HSV color ranges to detect
            min_area: Minimum contour area to consider as target
            max_area: Maximum contour area to consider as target
            blur_kernel: Kernel size for Gaussian blur (noise reduction)
        """
        self.color_ranges = color_ranges or [COLOR_PRESETS["red"], COLOR_PRESETS["red_alt"]]
        self.min_area = min_area
        self.max_area = max_area
        self.blur_kernel = blur_kernel

    def set_color_ranges(self, color_ranges: list[ColorRange]):
        """Update the color ranges to detect."""
        self.color_ranges = color_ranges

    def add_color_range(self, color_range: ColorRange):
        """Add a color range to detection."""
        self.color_ranges.append(color_range)

    def detect(self, frame: np.ndarray) -> list[Target]:
        """
        Detect targets in the frame.

        Args:
            frame: BGR image as numpy array

        Returns:
            List of detected targets, sorted by distance from center
        """
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2

        # Apply blur to reduce noise
        if self.blur_kernel > 1:
            frame = cv2.GaussianBlur(frame, (self.blur_kernel, self.blur_kernel), 0)

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create combined mask for all color ranges
        combined_mask = np.zeros((height, width), dtype=np.uint8)

        for color_range in self.color_ranges:
            mask = cv2.inRange(hsv, color_range.lower, color_range.upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)

        # Morphological operations to clean up mask
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        targets = []
        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate center of target
            target_center_x = x + w // 2
            target_center_y = y + h // 2

            # Calculate distance from crosshair (center of capture region)
            distance = np.sqrt((target_center_x - center_x) ** 2 + (target_center_y - center_y) ** 2)

            targets.append(Target(
                x=target_center_x,
                y=target_center_y,
                width=w,
                height=h,
                area=area,
                distance_from_center=distance,
            ))

        # Sort by distance from center (closest first)
        targets.sort(key=lambda t: t.distance_from_center)

        return targets

    def detect_closest(self, frame: np.ndarray) -> Optional[Target]:
        """
        Detect and return only the closest target to center.

        Args:
            frame: BGR image as numpy array

        Returns:
            Closest target or None if no targets found
        """
        targets = self.detect(frame)
        return targets[0] if targets else None

    def get_debug_frame(self, frame: np.ndarray, targets: list[Target]) -> np.ndarray:
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

        return debug_frame
