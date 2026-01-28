"""
Configuration settings for the aim assist.
Modify these values to tune the aim assist for your game.
"""

from dataclasses import dataclass, field
from typing import Optional
import json
import os


@dataclass
class AimAssistConfig:
    """Configuration for aim assist behavior."""

    # Screen capture settings
    capture_width: int = 320  # Width of detection area (centered on screen)
    capture_height: int = 320  # Height of detection area
    monitor_index: int = 1  # Monitor to capture (1 = primary)

    # Target detection settings
    detection_mode: str = "motion"  # "color" or "motion"
    target_color: str = "red"  # Color preset name or "custom" (for color mode)
    custom_hsv_lower: tuple[int, int, int] = (0, 100, 100)  # For custom color
    custom_hsv_upper: tuple[int, int, int] = (10, 255, 255)  # For custom color
    min_target_area: int = 100  # Minimum pixel area to consider
    max_target_area: int = 50000  # Maximum pixel area to consider
    motion_threshold: int = 25  # Sensitivity for motion detection (lower = more sensitive)

    # Mouse control settings
    sensitivity: float = 0.8  # Aim speed multiplier (0.1 - 5.0)
    smoothing: float = 0.3  # Movement smoothing (0.0 - 1.0, higher = smoother)
    max_speed: int = 80  # Max pixels per frame movement
    deadzone: int = 3  # Ignore targets this close to crosshair

    # Aim behavior
    aim_at_head: bool = True  # Offset aim upward for headshots
    head_offset_ratio: float = 0.35  # How far up to aim (0.0 - 1.0)
    fov_limit: int = 150  # Max distance to lock onto targets

    # Activation settings
    activation_key: str = "right_click"  # Hold to activate (right_click, shift, ctrl, alt, mouse4, mouse5)
    toggle_key: str = "capslock"  # Toggle aim assist on/off
    exit_key: str = "end"  # Exit the program

    # Performance settings
    target_fps: int = 120  # Target loop rate
    use_prediction: bool = False  # Enable target movement prediction

    # Debug settings
    debug_mode: bool = False  # Show debug window with detections
    show_fps: bool = True  # Show FPS counter in debug mode

    def save(self, filepath: str = "aim_config.json"):
        """Save configuration to JSON file."""
        config_dict = {
            "capture_width": self.capture_width,
            "capture_height": self.capture_height,
            "monitor_index": self.monitor_index,
            "detection_mode": self.detection_mode,
            "target_color": self.target_color,
            "custom_hsv_lower": list(self.custom_hsv_lower),
            "custom_hsv_upper": list(self.custom_hsv_upper),
            "min_target_area": self.min_target_area,
            "max_target_area": self.max_target_area,
            "motion_threshold": self.motion_threshold,
            "sensitivity": self.sensitivity,
            "smoothing": self.smoothing,
            "max_speed": self.max_speed,
            "deadzone": self.deadzone,
            "aim_at_head": self.aim_at_head,
            "head_offset_ratio": self.head_offset_ratio,
            "fov_limit": self.fov_limit,
            "activation_key": self.activation_key,
            "toggle_key": self.toggle_key,
            "exit_key": self.exit_key,
            "target_fps": self.target_fps,
            "use_prediction": self.use_prediction,
            "debug_mode": self.debug_mode,
            "show_fps": self.show_fps,
        }
        with open(filepath, "w") as f:
            json.dump(config_dict, f, indent=2)

    @classmethod
    def load(cls, filepath: str = "aim_config.json") -> "AimAssistConfig":
        """Load configuration from JSON file."""
        if not os.path.exists(filepath):
            return cls()

        with open(filepath, "r") as f:
            config_dict = json.load(f)

        return cls(
            capture_width=config_dict.get("capture_width", 320),
            capture_height=config_dict.get("capture_height", 320),
            monitor_index=config_dict.get("monitor_index", 1),
            detection_mode=config_dict.get("detection_mode", "motion"),
            target_color=config_dict.get("target_color", "red"),
            custom_hsv_lower=tuple(config_dict.get("custom_hsv_lower", [0, 100, 100])),
            custom_hsv_upper=tuple(config_dict.get("custom_hsv_upper", [10, 255, 255])),
            min_target_area=config_dict.get("min_target_area", 100),
            max_target_area=config_dict.get("max_target_area", 50000),
            motion_threshold=config_dict.get("motion_threshold", 25),
            sensitivity=config_dict.get("sensitivity", 0.8),
            smoothing=config_dict.get("smoothing", 0.3),
            max_speed=config_dict.get("max_speed", 80),
            deadzone=config_dict.get("deadzone", 3),
            aim_at_head=config_dict.get("aim_at_head", True),
            head_offset_ratio=config_dict.get("head_offset_ratio", 0.35),
            fov_limit=config_dict.get("fov_limit", 150),
            activation_key=config_dict.get("activation_key", "shift"),
            toggle_key=config_dict.get("toggle_key", "capslock"),
            exit_key=config_dict.get("exit_key", "end"),
            target_fps=config_dict.get("target_fps", 120),
            use_prediction=config_dict.get("use_prediction", False),
            debug_mode=config_dict.get("debug_mode", False),
            show_fps=config_dict.get("show_fps", True),
        )
