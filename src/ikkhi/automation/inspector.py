"""
Universal Windows UI Inspector.
Dynamically discovers and indexes interactive controls across any foreground Windows application.
"""

import ctypes
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ikkhi.automation.profiles import IndexedControl


@dataclass
class WindowContext:
    hwnd: int
    title: str
    process_name: str
    pid: int
    bounding_box: Tuple[int, int, int, int] # (left, top, right, bottom)


class UniversalUIInspector:
    """Introspects any foreground Windows process and inspects its accessibility hierarchy."""

    def get_foreground_context(self) -> Optional[WindowContext]:
        """Queries the current active foreground window, title, and executable process."""
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None

        # Extract Window Title
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value

        # Extract PID & Process Name
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process_name = self._get_process_name_by_pid(pid.value) or "unknown_app"

        # Bounding box
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        box = (rect.left, rect.top, rect.right, rect.bottom)

        return WindowContext(
            hwnd=hwnd,
            title=title,
            process_name=process_name,
            pid=pid.value,
            bounding_box=box
        )

    def _get_process_name_by_pid(self, pid: int) -> Optional[str]:
        """Query executable filename associated with the target process ID."""
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        kernel32 = ctypes.windll.kernel32
        h_process = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h_process:
            return None

        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_ulong(1024)
            if kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
                full_path = buf.value
                return os.path.basename(full_path)
            return None
        finally:
            kernel32.CloseHandle(h_process)

    def inspect_controls(self, hwnd: int, max_depth: int = 3) -> Dict[str, IndexedControl]:
        """
        Scans the accessible UI elements for the given window handle.
        Returns a dictionary of controls keyed by normalized control name/label.
        """
        discovered: Dict[str, IndexedControl] = {}
        try:
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=hwnd)
            window = app.window(handle=hwnd)
            
            # Enumerate descendants up to max_depth
            elements = window.descendants()
            win_rect = window.rectangle()
            win_w = max(1, win_rect.width())
            win_h = max(1, win_rect.height())

            for elem in elements[:150]: # Cap iteration to preserve high performance
                try:
                    name = elem.window_text().strip()
                    ctrl_type = elem.element_info.control_type or "Unknown"
                    if not name or len(name) < 2:
                        continue

                    # Filter for interactive element types
                    if ctrl_type in ("Button", "MenuItem", "TabItem", "CheckBox", "RadioButton", "Hyperlink"):
                        rect = elem.rectangle()
                        # Calculate relative center within the window
                        center_x = (rect.left + rect.right) / 2
                        center_y = (rect.top + rect.bottom) / 2
                        norm_x = max(0.0, min(1.0, (center_x - win_rect.left) / win_w))
                        norm_y = max(0.0, min(1.0, (center_y - win_rect.top) / win_h))

                        clean_key = name.lower()
                        discovered[clean_key] = IndexedControl(
                            name=name,
                            control_type=ctrl_type,
                            automation_id=elem.element_info.automation_id or None,
                            bounding_box=(rect.left, rect.top, rect.right, rect.bottom),
                            relative_center=(norm_x, norm_y)
                        )
                except Exception:
                    continue
        except Exception:
            pass

        return discovered
