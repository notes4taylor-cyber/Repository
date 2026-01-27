"""
Main aim assist controller.
Combines screen capture, target detection, and mouse control into a cohesive system.
"""

import time
import threading
import cv2
import numpy as np
from pynput import keyboard, mouse
from typing import Optional

from screen_capture import ScreenCapture
from target_detector import TargetDetector, ColorRange, COLOR_PRESETS
from mouse_controller import AdvancedMouseController
from config import AimAssistConfig


class AimAssist:
    def __init__(self, config: Optional[AimAssistConfig] = None):
        """
        Initialize the aim assist system.

        Args:
            config: Configuration settings (uses defaults if None)
        """
        self.config = config or AimAssistConfig()

        # Initialize components
        self.screen_capture = ScreenCapture(
            capture_width=self.config.capture_width,
            capture_height=self.config.capture_height,
            monitor_index=self.config.monitor_index,
        )

        self.target_detector = TargetDetector(
            color_ranges=self._get_color_ranges(),
            min_area=self.config.min_target_area,
            max_area=self.config.max_target_area,
        )

        self.mouse_controller = AdvancedMouseController(
            sensitivity=self.config.sensitivity,
            smoothing=self.config.smoothing,
            max_speed=self.config.max_speed,
            deadzone=self.config.deadzone,
            fov_limit=self.config.fov_limit,
        )

        # State
        self.running = False
        self.enabled = True  # Master toggle
        self.active = False  # Currently aiming (activation key held)

        # Key states
        self._activation_key_held = False
        self._keys_pressed = set()

        # Performance tracking
        self.fps = 0
        self._frame_times: list[float] = []

        # Thread management
        self._main_thread: Optional[threading.Thread] = None
        self._input_listener_keyboard: Optional[keyboard.Listener] = None
        self._input_listener_mouse: Optional[mouse.Listener] = None

    def _get_color_ranges(self) -> list[ColorRange]:
        """Get color ranges based on config."""
        if self.config.target_color == "custom":
            return [ColorRange(
                lower=np.array(self.config.custom_hsv_lower),
                upper=np.array(self.config.custom_hsv_upper),
                name="custom",
            )]

        color = self.config.target_color.lower()

        # Handle red specially (wraps around hue)
        if color == "red":
            return [COLOR_PRESETS["red"], COLOR_PRESETS["red_alt"]]

        if color in COLOR_PRESETS:
            return [COLOR_PRESETS[color]]

        # Default to red
        return [COLOR_PRESETS["red"], COLOR_PRESETS["red_alt"]]

    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            return

        if key_name is None:
            return

        key_name = key_name.lower()
        self._keys_pressed.add(key_name)

        # Check activation key
        activation = self.config.activation_key.lower()
        if key_name == activation or (activation == "shift" and key_name in ("shift", "shift_r", "shift_l")):
            self._activation_key_held = True

        # Check toggle key
        if key_name == self.config.toggle_key.lower():
            self.enabled = not self.enabled
            status = "ENABLED" if self.enabled else "DISABLED"
            print(f"[AimAssist] {status}")

        # Check exit key
        if key_name == self.config.exit_key.lower():
            print("[AimAssist] Exit key pressed, stopping...")
            self.stop()

    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            key_name = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            return

        if key_name is None:
            return

        key_name = key_name.lower()
        self._keys_pressed.discard(key_name)

        # Check activation key
        activation = self.config.activation_key.lower()
        if key_name == activation or (activation == "shift" and key_name in ("shift", "shift_r", "shift_l")):
            self._activation_key_held = False
            self.mouse_controller.reset_smoothing()

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse button events for activation."""
        activation = self.config.activation_key.lower()
        button_name = button.name.lower() if hasattr(button, 'name') else str(button)

        # Right click activation
        if activation == "right_click":
            if button_name == "right":
                self._activation_key_held = pressed
                if not pressed:
                    self.mouse_controller.reset_smoothing()

        # Side mouse button activation (mouse4/mouse5)
        elif activation in ("mouse4", "mouse5", "x1", "x2"):
            if button_name in ("x1", "x2", "button8", "button9"):
                self._activation_key_held = pressed
                if not pressed:
                    self.mouse_controller.reset_smoothing()

    def _main_loop(self):
        """Main aim assist loop."""
        target_frame_time = 1.0 / self.config.target_fps

        while self.running:
            loop_start = time.perf_counter()

            # Check if active
            self.active = self.enabled and self._activation_key_held

            if self.active:
                # Capture screen
                frame = self.screen_capture.capture()

                # Detect target
                target = self.target_detector.detect_closest(frame)

                if target:
                    # Calculate offset from center
                    frame_center_x = self.config.capture_width // 2
                    frame_center_y = self.config.capture_height // 2

                    offset_x = target.x - frame_center_x
                    offset_y = target.y - frame_center_y

                    # Move mouse
                    self.mouse_controller.move_to_target(
                        offset_x=offset_x,
                        offset_y=offset_y,
                        aim_at_head=self.config.aim_at_head,
                        head_offset_ratio=self.config.head_offset_ratio,
                        use_prediction=self.config.use_prediction,
                    )

                # Debug visualization
                if self.config.debug_mode:
                    targets = self.target_detector.detect(frame)
                    debug_frame = self.target_detector.get_debug_frame(frame, targets)

                    if self.config.show_fps:
                        cv2.putText(
                            debug_frame,
                            f"FPS: {self.fps:.0f}",
                            (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            1,
                        )
                        status = "ACTIVE" if self.active else "STANDBY"
                        cv2.putText(
                            debug_frame,
                            f"Status: {status}",
                            (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0) if self.active else (0, 165, 255),
                            1,
                        )

                    cv2.imshow("Aim Assist Debug", debug_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop()
                        break

            elif self.config.debug_mode:
                # Show standby frame in debug mode
                frame = self.screen_capture.capture()
                debug_frame = frame.copy()
                cv2.putText(
                    debug_frame,
                    f"FPS: {self.fps:.0f} | STANDBY (hold {self.config.activation_key})",
                    (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 165, 255),
                    1,
                )
                cv2.imshow("Aim Assist Debug", debug_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break

            # Calculate FPS
            frame_time = time.perf_counter() - loop_start
            self._frame_times.append(frame_time)
            if len(self._frame_times) > 60:
                self._frame_times.pop(0)
            avg_frame_time = sum(self._frame_times) / len(self._frame_times)
            self.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0

            # Sleep to maintain target FPS
            sleep_time = target_frame_time - frame_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def start(self):
        """Start the aim assist."""
        if self.running:
            return

        print("[AimAssist] Starting...")
        print(f"[AimAssist] Hold '{self.config.activation_key}' to activate")
        print(f"[AimAssist] Press '{self.config.toggle_key}' to toggle on/off")
        print(f"[AimAssist] Press '{self.config.exit_key}' to exit")

        self.running = True

        # Start input listeners
        self._input_listener_keyboard = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._input_listener_keyboard.start()

        self._input_listener_mouse = mouse.Listener(
            on_click=self._on_mouse_click,
        )
        self._input_listener_mouse.start()

        # Start main loop in thread
        self._main_thread = threading.Thread(target=self._main_loop, daemon=True)
        self._main_thread.start()

        print("[AimAssist] Running! (Debug mode:", "ON" if self.config.debug_mode else "OFF", ")")

    def run(self):
        """Start and block until stopped."""
        self.start()
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the aim assist."""
        self.running = False

        if self._input_listener_keyboard:
            self._input_listener_keyboard.stop()
        if self._input_listener_mouse:
            self._input_listener_mouse.stop()

        self.screen_capture.close()

        if self.config.debug_mode:
            cv2.destroyAllWindows()

        print("[AimAssist] Stopped.")

    def update_config(self, config: AimAssistConfig):
        """Update configuration (can be called while running)."""
        self.config = config

        # Update components
        self.screen_capture.set_capture_size(
            config.capture_width,
            config.capture_height,
        )

        self.target_detector.set_color_ranges(self._get_color_ranges())
        self.target_detector.min_area = config.min_target_area
        self.target_detector.max_area = config.max_target_area

        self.mouse_controller.set_sensitivity(config.sensitivity)
        self.mouse_controller.set_smoothing(config.smoothing)
        self.mouse_controller.max_speed = config.max_speed
        self.mouse_controller.deadzone = config.deadzone
        self.mouse_controller.fov_limit = config.fov_limit


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Vision-based aim assist")
    parser.add_argument("--config", "-c", type=str, help="Path to config file")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    parser.add_argument("--color", type=str, help="Target color preset (red, yellow, green, etc.)")
    parser.add_argument("--sensitivity", "-s", type=float, help="Aim sensitivity (0.1-5.0)")

    args = parser.parse_args()

    # Load or create config
    if args.config:
        config = AimAssistConfig.load(args.config)
    else:
        config = AimAssistConfig()

    # Apply command line overrides
    if args.debug:
        config.debug_mode = True
    if args.color:
        config.target_color = args.color
    if args.sensitivity:
        config.sensitivity = args.sensitivity

    # Create and run
    aim_assist = AimAssist(config)
    aim_assist.run()


if __name__ == "__main__":
    main()
