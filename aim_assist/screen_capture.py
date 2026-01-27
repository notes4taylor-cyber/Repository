"""
Screen capture module using MSS for fast screen grabbing.
Captures a region around the center of the screen (where crosshair typically is).
"""

import numpy as np
import mss
import mss.tools


class ScreenCapture:
    def __init__(self, capture_width: int = 320, capture_height: int = 320, monitor_index: int = 1):
        """
        Initialize screen capture.

        Args:
            capture_width: Width of capture region in pixels
            capture_height: Height of capture region in pixels
            monitor_index: Monitor to capture from (1 = primary)
        """
        self.capture_width = capture_width
        self.capture_height = capture_height
        self.monitor_index = monitor_index
        self.sct = mss.mss()
        self._update_capture_region()

    def _update_capture_region(self):
        """Calculate the capture region centered on screen."""
        monitor = self.sct.monitors[self.monitor_index]
        self.screen_width = monitor["width"]
        self.screen_height = monitor["height"]
        self.screen_left = monitor["left"]
        self.screen_top = monitor["top"]

        # Center of screen
        self.center_x = self.screen_left + self.screen_width // 2
        self.center_y = self.screen_top + self.screen_height // 2

        # Capture region (centered)
        self.capture_region = {
            "left": self.center_x - self.capture_width // 2,
            "top": self.center_y - self.capture_height // 2,
            "width": self.capture_width,
            "height": self.capture_height,
        }

    def set_capture_size(self, width: int, height: int):
        """Update capture region size."""
        self.capture_width = width
        self.capture_height = height
        self._update_capture_region()

    def capture(self) -> np.ndarray:
        """
        Capture the screen region.

        Returns:
            numpy array of shape (height, width, 3) in BGR format
        """
        screenshot = self.sct.grab(self.capture_region)
        # Convert to numpy array (BGRA format from mss)
        frame = np.array(screenshot)
        # Convert BGRA to BGR (drop alpha channel)
        frame = frame[:, :, :3]
        return frame

    def capture_full_screen(self) -> np.ndarray:
        """Capture the entire screen."""
        monitor = self.sct.monitors[self.monitor_index]
        screenshot = self.sct.grab(monitor)
        frame = np.array(screenshot)
        frame = frame[:, :, :3]
        return frame

    def get_screen_center(self) -> tuple[int, int]:
        """Return screen center coordinates."""
        return (self.center_x, self.center_y)

    def get_capture_offset(self) -> tuple[int, int]:
        """Return top-left corner of capture region in screen coordinates."""
        return (self.capture_region["left"], self.capture_region["top"])

    def close(self):
        """Clean up resources."""
        self.sct.close()
