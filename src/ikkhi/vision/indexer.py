"""
Smart Screen Indexer & Token Optimizer.
Crops the active window, downsamples resolution, and formats images to maximize Gemini credit efficiency.
"""

import io
import ctypes
from dataclasses import dataclass
from typing import Tuple, Optional
from PIL import Image, ImageGrab
from ikkhi.core.config import ScreenIndexingSettings
from ikkhi.core.exceptions import ScreenCaptureError
from ikkhi.vision.monitors import MultiMonitorManager


@dataclass
class IndexedScreen:
    image_bytes: bytes
    mime_type: str
    original_window_box: Tuple[int, int, int, int] # (left, top, right, bottom)
    scaled_dimensions: Tuple[int, int]              # (width, height)
    scale_factor_x: float
    scale_factor_y: float
    monitor_index: int = 0

    def map_to_screen_coordinates(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """Convert normalized (0.0-1.0) coordinates within the crop back to absolute desktop pixels."""
        left, top, right, bottom = self.original_window_box
        win_w = right - left
        win_h = bottom - top
        abs_x = int(left + (norm_x * win_w))
        abs_y = int(top + (norm_y * win_h))
        return abs_x, abs_y


class ScreenIndexer:
    """Extracts credit-optimized visual snapshots of active applications across multi-display topologies."""

    def __init__(self, settings: ScreenIndexingSettings) -> None:
        self.settings = settings
        self.monitor_mgr = MultiMonitorManager()

    def capture_active_window(self) -> IndexedScreen:
        """Captures only the active window and compresses it to minimize multimodal API tokens."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            active_monitor = self.monitor_mgr.get_cursor_monitor()
            
            if not hwnd or not self.settings.crop_active_window_only:
                # Fallback to current monitor bounding box rather than whole virtual multi-monitor canvas
                box = (active_monitor.left, active_monitor.top, active_monitor.right, active_monitor.bottom)
            else:
                rect = ctypes.wintypes.RECT()
                ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                box = (rect.left, rect.top, rect.right, rect.bottom)
                # If window is minimized or has zero size, capture current monitor bounds
                if box[2] <= box[0] or box[3] <= box[1]:
                    box = (active_monitor.left, active_monitor.top, active_monitor.right, active_monitor.bottom)

            try:
                raw_image = ImageGrab.grab(bbox=box, all_screens=True)
            except Exception:
                try:
                    full_image = ImageGrab.grab(all_screens=True)
                    if box and box[2] > box[0] and box[3] > box[1]:
                        raw_image = full_image.crop(box)
                    else:
                        raw_image = full_image
                except Exception as grab_err:
                    raise ScreenCaptureError(f"Failed to capture screen: {grab_err}") from grab_err

            orig_w, orig_h = raw_image.size
            if box is None:
                box = (0, 0, orig_w, orig_h)

            # Credit Saver: Downscale if image exceeds max dimension
            max_dim = self.settings.max_image_dimension
            if max(orig_w, orig_h) > max_dim:
                if orig_w >= orig_h:
                    new_w = max_dim
                    new_h = int(orig_h * (max_dim / orig_w))
                else:
                    new_h = max_dim
                    new_w = int(orig_w * (max_dim / orig_h))
                scaled_image = raw_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                scaled_image = raw_image
                new_w, new_h = orig_w, orig_h

            buffer = io.BytesIO()
            scaled_image.convert("RGB").save(
                buffer,
                format="JPEG",
                quality=self.settings.jpeg_quality,
                optimize=True
            )
            image_bytes = buffer.getvalue()

            return IndexedScreen(
                image_bytes=image_bytes,
                mime_type="image/jpeg",
                original_window_box=box,
                scaled_dimensions=(new_w, new_h),
                scale_factor_x=new_w / orig_w,
                scale_factor_y=new_h / orig_h
            )
        except Exception as exc:
            raise ScreenCaptureError(f"Failed to capture and index screen: {exc}") from exc
