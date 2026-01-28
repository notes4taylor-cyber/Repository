#!/usr/bin/env python3
"""
E-Key Mouse Macro
Press 'E' to toggle rapid left/right mouse clicking.
Press 'Esc' to exit the program.
"""

import threading
import time
from pynput import keyboard, mouse

# Configuration
CLICK_DELAY = 0.05  # Seconds between clicks (adjust for faster/slower)

# State
clicking = False
click_thread = None
mouse_controller = mouse.Controller()


def click_loop():
    """Continuously clicks left and right mouse buttons while enabled."""
    while clicking:
        mouse_controller.click(mouse.Button.left)
        time.sleep(CLICK_DELAY)
        mouse_controller.click(mouse.Button.right)
        time.sleep(CLICK_DELAY)


def toggle_clicking():
    """Toggle the clicking on/off."""
    global clicking, click_thread

    if clicking:
        clicking = False
        print("Clicking STOPPED")
    else:
        clicking = True
        print("Clicking STARTED")
        click_thread = threading.Thread(target=click_loop, daemon=True)
        click_thread.start()


def on_press(key):
    """Handle key press events."""
    try:
        if key.char == 'e':
            toggle_clicking()
    except AttributeError:
        # Special key pressed
        if key == keyboard.Key.esc:
            global clicking
            clicking = False
            print("Exiting...")
            return False  # Stop listener


def main():
    print("=" * 40)
    print("E-Key Mouse Macro")
    print("=" * 40)
    print("Press 'E' to toggle mouse click spam")
    print("Press 'Esc' to exit")
    print("=" * 40)

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
