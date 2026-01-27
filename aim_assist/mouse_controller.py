"""
Mouse control module for smooth aim movement.
Uses relative mouse movement for game compatibility.
"""

import time
import math
from typing import Optional
from pynput.mouse import Controller as MouseControllerBackend


class MouseController:
    def __init__(
        self,
        sensitivity: float = 1.0,
        smoothing: float = 0.5,
        max_speed: int = 100,
        deadzone: int = 5,
    ):
        """
        Initialize mouse controller.

        Args:
            sensitivity: Movement multiplier (higher = faster aim)
            smoothing: Smoothing factor 0-1 (higher = smoother but slower)
            max_speed: Maximum pixels to move per update
            deadzone: Minimum distance to target before moving (prevents jitter)
        """
        self.sensitivity = sensitivity
        self.smoothing = smoothing
        self.max_speed = max_speed
        self.deadzone = deadzone
        self._mouse = MouseControllerBackend()

        # For smoothing calculations
        self._last_move_x = 0.0
        self._last_move_y = 0.0

    def set_sensitivity(self, sensitivity: float):
        """Update sensitivity."""
        self.sensitivity = max(0.1, min(5.0, sensitivity))

    def set_smoothing(self, smoothing: float):
        """Update smoothing factor."""
        self.smoothing = max(0.0, min(1.0, smoothing))

    def move_to_target(
        self,
        offset_x: int,
        offset_y: int,
        aim_at_head: bool = True,
        head_offset_ratio: float = 0.3,
    ) -> bool:
        """
        Move mouse towards target offset from center.

        Args:
            offset_x: Horizontal offset from crosshair to target (positive = right)
            offset_y: Vertical offset from crosshair to target (positive = down)
            aim_at_head: If True, aim slightly above center (for headshots)
            head_offset_ratio: How much to offset upward (0-1, percentage of target height)

        Returns:
            True if movement was made, False if within deadzone
        """
        # Apply head offset if enabled
        if aim_at_head:
            # This assumes we're given the center of the target
            # Offset upward to aim at head region
            offset_y = int(offset_y * (1 - head_offset_ratio))

        # Calculate distance
        distance = math.sqrt(offset_x ** 2 + offset_y ** 2)

        # Check deadzone
        if distance < self.deadzone:
            self._last_move_x = 0
            self._last_move_y = 0
            return False

        # Apply sensitivity
        move_x = offset_x * self.sensitivity
        move_y = offset_y * self.sensitivity

        # Apply smoothing (exponential moving average)
        if self.smoothing > 0:
            move_x = move_x * (1 - self.smoothing) + self._last_move_x * self.smoothing
            move_y = move_y * (1 - self.smoothing) + self._last_move_y * self.smoothing

        # Clamp to max speed
        move_distance = math.sqrt(move_x ** 2 + move_y ** 2)
        if move_distance > self.max_speed:
            scale = self.max_speed / move_distance
            move_x *= scale
            move_y *= scale

        # Store for next smoothing calculation
        self._last_move_x = move_x
        self._last_move_y = move_y

        # Perform relative mouse move using pynput
        int_move_x = int(round(move_x))
        int_move_y = int(round(move_y))

        if int_move_x != 0 or int_move_y != 0:
            self._mouse.move(int_move_x, int_move_y)
            return True

        return False

    def move_relative(self, dx: int, dy: int):
        """Direct relative mouse movement without smoothing."""
        self._mouse.move(dx, dy)

    def reset_smoothing(self):
        """Reset smoothing state (call when toggling aim assist off/on)."""
        self._last_move_x = 0.0
        self._last_move_y = 0.0


class AdvancedMouseController(MouseController):
    """
    Advanced mouse controller with additional features like
    acceleration curves and prediction.
    """

    def __init__(
        self,
        sensitivity: float = 1.0,
        smoothing: float = 0.5,
        max_speed: int = 100,
        deadzone: int = 5,
        acceleration_curve: float = 1.0,
        fov_limit: int = 150,
    ):
        """
        Initialize advanced mouse controller.

        Args:
            sensitivity: Base movement multiplier
            smoothing: Smoothing factor 0-1
            max_speed: Maximum pixels to move per update
            deadzone: Minimum distance threshold
            acceleration_curve: Exponent for distance-based acceleration (1.0 = linear)
            fov_limit: Maximum distance (FOV) to consider targets
        """
        super().__init__(sensitivity, smoothing, max_speed, deadzone)
        self.acceleration_curve = acceleration_curve
        self.fov_limit = fov_limit

        # For prediction
        self._target_history: list[tuple[int, int, float]] = []
        self._max_history = 5

    def move_to_target(
        self,
        offset_x: int,
        offset_y: int,
        aim_at_head: bool = True,
        head_offset_ratio: float = 0.3,
        use_prediction: bool = False,
    ) -> bool:
        """
        Move mouse towards target with advanced features.

        Args:
            offset_x: Horizontal offset from crosshair
            offset_y: Vertical offset from crosshair
            aim_at_head: Aim at head region
            head_offset_ratio: Head offset amount
            use_prediction: Enable target movement prediction

        Returns:
            True if movement was made
        """
        # Calculate distance
        distance = math.sqrt(offset_x ** 2 + offset_y ** 2)

        # Check FOV limit
        if distance > self.fov_limit:
            return False

        # Check deadzone
        if distance < self.deadzone:
            self._last_move_x = 0
            self._last_move_y = 0
            return False

        # Apply head offset
        if aim_at_head:
            offset_y = int(offset_y * (1 - head_offset_ratio))

        # Apply prediction if enabled
        if use_prediction:
            pred_x, pred_y = self._predict_target(offset_x, offset_y)
            offset_x += int(pred_x)
            offset_y += int(pred_y)

        # Apply acceleration curve (smaller movements get scaled down more)
        normalized_distance = min(distance / self.fov_limit, 1.0)
        acceleration = normalized_distance ** self.acceleration_curve

        # Apply sensitivity with acceleration
        move_x = offset_x * self.sensitivity * acceleration
        move_y = offset_y * self.sensitivity * acceleration

        # Apply smoothing
        if self.smoothing > 0:
            move_x = move_x * (1 - self.smoothing) + self._last_move_x * self.smoothing
            move_y = move_y * (1 - self.smoothing) + self._last_move_y * self.smoothing

        # Clamp to max speed
        move_distance = math.sqrt(move_x ** 2 + move_y ** 2)
        if move_distance > self.max_speed:
            scale = self.max_speed / move_distance
            move_x *= scale
            move_y *= scale

        self._last_move_x = move_x
        self._last_move_y = move_y

        # Store for prediction
        self._target_history.append((offset_x, offset_y, time.time()))
        if len(self._target_history) > self._max_history:
            self._target_history.pop(0)

        # Perform movement using pynput
        int_move_x = int(round(move_x))
        int_move_y = int(round(move_y))

        if int_move_x != 0 or int_move_y != 0:
            self._mouse.move(int_move_x, int_move_y)
            return True

        return False

    def _predict_target(self, current_x: int, current_y: int) -> tuple[float, float]:
        """
        Predict target movement based on history.

        Returns:
            Predicted offset to add to current position
        """
        if len(self._target_history) < 2:
            return (0.0, 0.0)

        # Calculate velocity from recent history
        recent = self._target_history[-3:]  # Last 3 positions

        if len(recent) < 2:
            return (0.0, 0.0)

        # Average velocity
        total_dx = 0.0
        total_dy = 0.0
        total_dt = 0.0

        for i in range(1, len(recent)):
            dx = recent[i][0] - recent[i - 1][0]
            dy = recent[i][1] - recent[i - 1][1]
            dt = recent[i][2] - recent[i - 1][2]

            if dt > 0:
                total_dx += dx
                total_dy += dy
                total_dt += dt

        if total_dt == 0:
            return (0.0, 0.0)

        # Velocity per second
        vel_x = total_dx / total_dt
        vel_y = total_dy / total_dt

        # Predict ahead by ~16ms (one frame at 60fps)
        prediction_time = 0.016
        pred_x = vel_x * prediction_time
        pred_y = vel_y * prediction_time

        return (pred_x, pred_y)

    def reset_smoothing(self):
        """Reset all state."""
        super().reset_smoothing()
        self._target_history.clear()
