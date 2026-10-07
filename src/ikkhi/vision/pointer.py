"""
Visual cursor pointer & grounding engine.
Animates the cursor to visually guide the user's attention to targets on the screen.
"""

import time
import math
import ctypes
from typing import Tuple
import pyautogui
from ikkhi.core.config import PointerSettings


def _ease_out_cubic(t: float) -> float:
    return 1.0 - math.pow(1.0 - t, 3)


class CursorPointer:
    """Manages high-precision, smooth cursor guidance with DPI compensation."""

    def __init__(self, settings: PointerSettings) -> None:
        self.settings = settings
        self._init_dpi_awareness()

    def _init_dpi_awareness(self) -> None:
        """Ensure physical pixel coordinate accuracy on high-DPI (e.g. 4K) displays."""
        try:
            DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
            ctypes.windll.user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
        except Exception:
            pass

    def point_to(self, target_x: int, target_y: int) -> None:
        """Smoothly glides the mouse cursor to (target_x, target_y) and performs an attention pulse."""
        start_x, start_y = pyautogui.position()
        duration = self.settings.smooth_move_duration
        steps = max(15, int(duration * 60))
        sleep_interval = duration / steps

        # Smooth glide using cubic ease-out
        for step in range(1, steps + 1):
            t = step / steps
            eased_t = _ease_out_cubic(t)
            current_x = int(start_x + (target_x - start_x) * eased_t)
            current_y = int(start_y + (target_y - start_y) * eased_t)
            pyautogui.moveTo(current_x, current_y, _pause=False)
            time.sleep(sleep_interval)

        # Trigger HeyClicky-style on-screen visual ripple beacon
        try:
            from ikkhi.ui.beacon import show_visual_beacon
            show_visual_beacon(target_x, target_y, duration=self.settings.highlight_duration_seconds)
        except Exception:
            pass

        # Attention highlight: subtle circular gesture
        self._highlight_target(target_x, target_y)

    def _highlight_target(self, center_x: int, center_y: int) -> None:
        """Executes a micro-orbit around the target coordinate to attract the user's eye."""
        radius = 12
        steps = 12
        for i in range(steps):
            angle = (2 * math.pi * i) / steps
            ox = int(center_x + radius * math.cos(angle))
            oy = int(center_y + radius * math.sin(angle))
            pyautogui.moveTo(ox, oy, _pause=False)
            time.sleep(0.015)
        # Snap back to center
        pyautogui.moveTo(center_x, center_y, _pause=False)
