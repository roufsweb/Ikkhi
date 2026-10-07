"""
Smart Screen Indexer & Token Optimizer.
Crops the active window, downsamples resolution, compresses to WebP, and calculates live window coordinates
while enforcing privacy shields on credential managers and sensitive applications.
"""

import io
import os
import math
import ctypes
from dataclasses import dataclass
from typing import Tuple, Optional, Set
from PIL import Image, ImageGrab
from ikkhi.core.config import ScreenIndexingSettings
from ikkhi.core.exceptions import ScreenCaptureError, ScreenSecurityViolation
from ikkhi.vision.monitors import MultiMonitorManager

# Sensitive processes that must never have screen contents captured or routed to cloud AI
SENSITIVE_PROCESSES: Set[str] = {
    "bitwarden.exe",
    "1password.exe",
    "keepass.exe",
    "keepassxc.exe",
    "credentialmanager.exe",
    "dashlane.exe",
    "nordpass.exe",
    "enpass.exe",
    "roboform.exe",
    "authy.exe",
}

# Window title keywords triggering the privacy security shield
SENSITIVE_TITLE_KEYWORDS = [
    "password manager",
    "master password",
    "private key",
    "secret recovery phrase",
    "credit card",
    "bank login",
]


@dataclass
class IndexedScreen:
    image_bytes: bytes
    mime_type: str
    original_window_box: Tuple[int, int, int, int] # (left, top, right, bottom)
    scaled_dimensions: Tuple[int, int]              # (width, height)
    scale_factor_x: float
    scale_factor_y: float
    monitor_index: int = 0
    payload_kb: float = 0.0
    estimated_tokens: int = 258
    window_title: str = ""
    process_name: str = ""
    window_hwnd: int = 0

    def map_to_screen_coordinates(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """
        Convert normalized (0.0-1.0) coordinates within the crop back to absolute desktop pixels.
        If the target window is still active, recalculates live physical coordinates to account
        for window dragging, snapping, or floating movement.
        """
        if self.window_hwnd:
            user32 = ctypes.windll.user32
            if user32.IsWindow(self.window_hwnd) and not user32.IsIconic(self.window_hwnd):
                rect = ctypes.wintypes.RECT()
                if user32.GetWindowRect(self.window_hwnd, ctypes.byref(rect)):
                    live_w = rect.right - rect.left
                    live_h = rect.bottom - rect.top
                    if live_w > 0 and live_h > 0:
                        abs_x = int(rect.left + (norm_x * live_w))
                        abs_y = int(rect.top + (norm_y * live_h))
                        return abs_x, abs_y

        # Fallback to coordinates at time of capture
        left, top, right, bottom = self.original_window_box
        win_w = right - left
        win_h = bottom - top
        abs_x = int(left + (norm_x * win_w))
        abs_y = int(top + (norm_y * win_h))
        return abs_x, abs_y

    def bring_window_to_front(self) -> None:
        """Restores and brings the target window to the foreground if occluded."""
        if self.window_hwnd:
            user32 = ctypes.windll.user32
            if user32.IsWindow(self.window_hwnd):
                user32.ShowWindow(self.window_hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(self.window_hwnd)


class ScreenIndexer:
    """Extracts credit-optimized visual snapshots of active applications across multi-display topologies."""

    def __init__(self, settings: ScreenIndexingSettings) -> None:
        self.settings = settings
        self.monitor_mgr = MultiMonitorManager()

    def _get_window_context(self, hwnd: int) -> Tuple[str, str]:
        """Extracts process executable name and title for the given window handle."""
        if not hwnd:
            return "desktop", "Desktop"

        user32 = ctypes.windll.user32
        # Title
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.strip()

        # PID & Executable
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        process_name = "unknown_app"
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        kernel32 = ctypes.windll.kernel32
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if h_process:
            try:
                buf = ctypes.create_unicode_buffer(1024)
                size = ctypes.c_ulong(1024)
                if kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
                    process_name = os.path.basename(buf.value)
            finally:
                kernel32.CloseHandle(h_process)

        return process_name, title

    def _check_security_shield(self, process_name: str, title: str) -> None:
        """Shields sensitive apps from cloud multimodal screen indexing."""
        if not self.settings.security_shield_enabled:
            return

        p_lower = process_name.lower()
        if p_lower in SENSITIVE_PROCESSES:
            raise ScreenSecurityViolation(
                f"Visual screen capture blocked by security shield: Process '{process_name}' is protected."
            )

        t_lower = title.lower()
        for keyword in SENSITIVE_TITLE_KEYWORDS:
            if keyword in t_lower:
                raise ScreenSecurityViolation(
                    f"Visual screen capture blocked by security shield: Window title contains sensitive keyword '{keyword}'."
                )

    def capture_active_window(self) -> IndexedScreen:
        """Captures only the active window and compresses it into WebP to minimize multimodal API tokens."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            process_name, title = self._get_window_context(hwnd)
            self._check_security_shield(process_name, title)

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

            # Credit Saver: Downscale if image exceeds max dimension (clamped to 768px for 1 vision tile)
            max_dim = self.settings.max_image_dimension
            if max(orig_w, orig_h) > max_dim:
                if orig_w >= orig_h:
                    new_w = max_dim
                    new_h = max(1, int(orig_h * (max_dim / orig_w)))
                else:
                    new_h = max_dim
                    new_w = max(1, int(orig_w * (max_dim / orig_h)))
                scaled_image = raw_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                scaled_image = raw_image
                new_w, new_h = orig_w, orig_h

            # Format selection: Modern WebP compression for <80KB bandwidth vs legacy JPEG
            buffer = io.BytesIO()
            rgb_image = scaled_image.convert("RGB")
            
            if self.settings.image_format.upper() == "WEBP":
                mime_type = "image/webp"
                try:
                    rgb_image.save(buffer, format="WEBP", quality=self.settings.webp_quality, method=4)
                except Exception:
                    # Fallback to JPEG if libwebp is unavailable
                    buffer = io.BytesIO()
                    rgb_image.save(buffer, format="JPEG", quality=self.settings.jpeg_quality, optimize=True)
                    mime_type = "image/jpeg"
            else:
                mime_type = "image/jpeg"
                rgb_image.save(buffer, format="JPEG", quality=self.settings.jpeg_quality, optimize=True)

            image_bytes = buffer.getvalue()
            payload_kb = round(len(image_bytes) / 1024.0, 1)

            # Multimodal Vision Token Estimation: 258 tokens per 768x768 tile in Gemini models
            tiles_x = max(1, math.ceil(new_w / 768.0))
            tiles_y = max(1, math.ceil(new_h / 768.0))
            estimated_tokens = 258 * tiles_x * tiles_y

            return IndexedScreen(
                image_bytes=image_bytes,
                mime_type=mime_type,
                original_window_box=box,
                scaled_dimensions=(new_w, new_h),
                scale_factor_x=new_w / max(1, orig_w),
                scale_factor_y=new_h / max(1, orig_h),
                payload_kb=payload_kb,
                estimated_tokens=estimated_tokens,
                window_title=title,
                process_name=process_name,
                window_hwnd=hwnd or 0
            )
        except ScreenSecurityViolation:
            raise
        except Exception as exc:
            raise ScreenCaptureError(f"Failed to capture and index screen: {exc}") from exc

