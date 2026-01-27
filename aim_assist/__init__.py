"""
Vision-based aim assist package.
"""

from .aim_assist import AimAssist
from .config import AimAssistConfig
from .screen_capture import ScreenCapture
from .target_detector import TargetDetector, Target, ColorRange, COLOR_PRESETS
from .mouse_controller import MouseController, AdvancedMouseController

__all__ = [
    "AimAssist",
    "AimAssistConfig",
    "ScreenCapture",
    "TargetDetector",
    "Target",
    "ColorRange",
    "COLOR_PRESETS",
    "MouseController",
    "AdvancedMouseController",
]
