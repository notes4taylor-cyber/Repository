#!/usr/bin/env python3
"""
Color calibration tool for the aim assist.
Use this to find the HSV color values of targets in your game.

Instructions:
1. Run this script
2. Position your game so a target/enemy is visible
3. Click on the target color you want to detect
4. Adjust the tolerance slider to fine-tune detection
5. Press 'S' to save the calibrated color to config
6. Press 'Q' to quit
"""

import cv2
import numpy as np
import json
from screen_capture import ScreenCapture
from target_detector import TargetDetector, ColorRange
from config import AimAssistConfig


class ColorCalibrator:
    def __init__(self):
        self.screen_capture = ScreenCapture(capture_width=640, capture_height=480)
        self.selected_color_hsv = None
        self.selected_color_bgr = None
        self.tolerance = 30
        self.config = AimAssistConfig()

        # Window setup
        self.window_name = "Color Calibrator"
        cv2.namedWindow(self.window_name)
        cv2.createTrackbar("Tolerance", self.window_name, self.tolerance, 100, self._on_tolerance_change)
        cv2.createTrackbar("Min Area", self.window_name, 50, 1000, lambda x: None)
        cv2.setMouseCallback(self.window_name, self._on_mouse_click)

    def _on_tolerance_change(self, value):
        self.tolerance = max(5, value)

    def _on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if hasattr(self, '_current_frame') and self._current_frame is not None:
                # Get the BGR color at click position
                bgr = self._current_frame[y, x]
                self.selected_color_bgr = tuple(map(int, bgr))

                # Convert to HSV
                hsv_frame = cv2.cvtColor(self._current_frame, cv2.COLOR_BGR2HSV)
                hsv = hsv_frame[y, x]
                self.selected_color_hsv = tuple(map(int, hsv))

                print(f"Selected color - BGR: {self.selected_color_bgr}, HSV: {self.selected_color_hsv}")

    def _get_color_range(self):
        """Get current color range based on selection and tolerance."""
        if self.selected_color_hsv is None:
            return None

        h, s, v = self.selected_color_hsv
        h_tol = min(self.tolerance // 2, 20)
        s_tol = self.tolerance
        v_tol = self.tolerance

        lower = np.array([max(0, h - h_tol), max(0, s - s_tol), max(0, v - v_tol)])
        upper = np.array([min(179, h + h_tol), min(255, s + s_tol), min(255, v + v_tol)])

        return ColorRange(lower=lower, upper=upper, name="calibrated")

    def run(self):
        """Run the calibrator."""
        print("\n=== Color Calibrator ===")
        print("Instructions:")
        print("  - Click on the target color in your game")
        print("  - Adjust 'Tolerance' slider to refine detection")
        print("  - Press 'S' to save color to config")
        print("  - Press 'P' to print current HSV values")
        print("  - Press 'R' to reset selection")
        print("  - Press 'Q' to quit")
        print("========================\n")

        while True:
            # Capture frame
            frame = self.screen_capture.capture()
            self._current_frame = frame.copy()

            display_frame = frame.copy()
            min_area = cv2.getTrackbarPos("Min Area", self.window_name)

            # If color selected, show detection
            if self.selected_color_hsv is not None:
                color_range = self._get_color_range()
                detector = TargetDetector(
                    color_ranges=[color_range],
                    min_area=min_area,
                    max_area=50000,
                )

                targets = detector.detect(frame)
                display_frame = detector.get_debug_frame(frame, targets)

                # Show selected color info
                h, s, v = self.selected_color_hsv
                info_text = f"HSV: ({h}, {s}, {v}) | Tolerance: {self.tolerance} | Targets: {len(targets)}"
                cv2.putText(display_frame, info_text, (10, 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Draw color swatch
                swatch = np.zeros((30, 60, 3), dtype=np.uint8)
                swatch[:] = self.selected_color_bgr
                display_frame[30:60, 10:70] = swatch
                cv2.rectangle(display_frame, (10, 30), (70, 60), (255, 255, 255), 1)

            else:
                cv2.putText(display_frame, "Click on target color to select",
                           (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # Draw crosshair
            h, w = display_frame.shape[:2]
            cv2.line(display_frame, (w//2 - 15, h//2), (w//2 + 15, h//2), (0, 255, 0), 1)
            cv2.line(display_frame, (w//2, h//2 - 15), (w//2, h//2 + 15), (0, 255, 0), 1)

            cv2.imshow(self.window_name, display_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break

            elif key == ord('s'):
                if self.selected_color_hsv is not None:
                    self._save_config()
                else:
                    print("No color selected!")

            elif key == ord('p'):
                if self.selected_color_hsv is not None:
                    color_range = self._get_color_range()
                    print(f"\nCurrent HSV Color Range:")
                    print(f"  Lower: {list(color_range.lower)}")
                    print(f"  Upper: {list(color_range.upper)}")
                    print(f"  Min Area: {min_area}")

            elif key == ord('r'):
                self.selected_color_hsv = None
                self.selected_color_bgr = None
                print("Selection reset")

        self.screen_capture.close()
        cv2.destroyAllWindows()

    def _save_config(self):
        """Save calibrated color to config file."""
        color_range = self._get_color_range()
        min_area = cv2.getTrackbarPos("Min Area", self.window_name)

        self.config.target_color = "custom"
        self.config.custom_hsv_lower = tuple(map(int, color_range.lower))
        self.config.custom_hsv_upper = tuple(map(int, color_range.upper))
        self.config.min_target_area = min_area

        self.config.save("aim_config.json")
        print(f"\nConfiguration saved to aim_config.json")
        print(f"  HSV Lower: {self.config.custom_hsv_lower}")
        print(f"  HSV Upper: {self.config.custom_hsv_upper}")
        print(f"  Min Area: {min_area}")


def main():
    calibrator = ColorCalibrator()
    calibrator.run()


if __name__ == "__main__":
    main()
