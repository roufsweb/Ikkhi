"""
Multi-Monitor Management & Virtual Screen Coordinate Normalizer.
Handles arbitrary multi-display topologies, negative coordinate offsets, and DPI awareness.
"""

import ctypes
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class MonitorInfo:
    index: int
    is_primary: bool
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    def contains_point(self, x: int, y: int) -> bool:
        return self.left <= x < self.right and self.top <= y < self.bottom


class MultiMonitorManager:
    """Introspects Windows display topology and resolves coordinates across multi-screen setups."""

    def __init__(self) -> None:
        self._init_dpi_awareness()

    def _init_dpi_awareness(self) -> None:
        try:
            DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = ctypes.c_void_p(-4)
            ctypes.windll.user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
        except Exception:
            pass

    def get_all_monitors(self) -> List[MonitorInfo]:
        """Enumerates all active physical and virtual displays attached to the Windows host."""
        monitors: List[MonitorInfo] = []
        user32 = ctypes.windll.user32

        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.wintypes.RECT),
            ctypes.c_void_p
        )

        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            rect = lprcMonitor.contents
            # Check if primary monitor: MONITORINFOF_PRIMARY = 0x00000001
            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("rcMonitor", ctypes.wintypes.RECT),
                    ("rcWork", ctypes.wintypes.RECT),
                    ("dwFlags", ctypes.c_ulong)
                ]

            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi))
            is_primary = bool(mi.dwFlags & 1)

            idx = len(monitors)
            monitors.append(MonitorInfo(
                index=idx,
                is_primary=is_primary,
                left=rect.left,
                top=rect.top,
                right=rect.right,
                bottom=rect.bottom
            ))
            return 1

        user32.EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0)
        return monitors

    def get_monitor_for_point(self, x: int, y: int) -> Optional[MonitorInfo]:
        """Returns the specific monitor containing the given (x, y) coordinates."""
        for mon in self.get_all_monitors():
            if mon.contains_point(x, y):
                return mon
        return None

    def get_cursor_monitor(self) -> MonitorInfo:
        """Determines which physical monitor currently hosts the mouse cursor."""
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        mon = self.get_monitor_for_point(pt.x, pt.y)
        if mon:
            return mon

        # Fallback to primary monitor
        all_monitors = self.get_all_monitors()
        for m in all_monitors:
            if m.is_primary:
                return m
        return all_monitors[0] if all_monitors else MonitorInfo(0, True, 0, 0, 1920, 1080)

    def get_window_monitor(self, hwnd: int) -> Optional[MonitorInfo]:
        """Identifies which monitor hosts the primary region of the given window handle."""
        MONITOR_DEFAULTTONEAREST = 2
        hMon = ctypes.windll.user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
        if not hMon:
            return self.get_cursor_monitor()

        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
        return self.get_monitor_for_point(center_x, center_y) or self.get_cursor_monitor()
