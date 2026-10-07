"""
HeyClicky-Style Visual Cursor Beacon & Target Ripple Indicator for Ikkhi.
Renders an animated, translucent neon radar halo and crosshair at target coordinates
to visually orient the user without stealing window focus.
"""

import math
from typing import Optional
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPaintEvent
from PyQt6.QtWidgets import QWidget, QApplication


class CursorTargetBeacon(QWidget):
    """
    Translucent, frameless top-level indicator that renders an expanding
    neon-cyan / cyber-violet attention beacon directly over target screen coordinates.
    """

    def __init__(self, parent: Optional[QWidget] = None, size: int = 80) -> None:
        super().__init__(parent)
        self.beacon_size = size
        self.phase = 0.0
        self.fade_alpha = 1.0
        self.duration_ms = 1500
        self.elapsed_ms = 0
        self._anim_interval = 25  # 40 FPS

        self.setFixedSize(self.beacon_size, self.beacon_size)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self._timer = QTimer(self)
        self._timer.setInterval(self._anim_interval)
        self._timer.timeout.connect(self._step_animation)

    def trigger_at(self, screen_x: int, screen_y: int, duration_seconds: float = 1.5) -> None:
        """Position beacon centered over (screen_x, screen_y) and commence animated pulse."""
        self.duration_ms = int(duration_seconds * 1000)
        self.elapsed_ms = 0
        self.phase = 0.0
        self.fade_alpha = 1.0

        # Center the widget exactly on (screen_x, screen_y)
        half = self.beacon_size // 2
        self.move(screen_x - half, screen_y - half)
        self.show()
        self._timer.start()

    @pyqtSlot()
    def _step_animation(self) -> None:
        """Advance pulse phase, compute decay alpha, and repaint."""
        self.elapsed_ms += self._anim_interval
        self.phase += 0.12

        # Compute remaining opacity
        remaining_ratio = max(0.0, 1.0 - (self.elapsed_ms / self.duration_ms))
        self.fade_alpha = math.pow(remaining_ratio, 0.7)

        if self.elapsed_ms >= self.duration_ms:
            self._timer.stop()
            self.hide()
            self.close()
            return

        self.update()

    def paintEvent(self, event: Optional[QPaintEvent]) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2.0
        center_y = self.height() / 2.0
        max_radius = (self.beacon_size / 2.0) - 4.0

        # Pulsating outer halo radius (expands continuously)
        pulse_cycle = (self.phase % (2 * math.pi)) / (2 * math.pi)
        outer_radius = 10.0 + pulse_cycle * (max_radius - 10.0)
        outer_alpha = int(220 * (1.0 - pulse_cycle) * self.fade_alpha)

        # 1. Outer Expanding Ripple Ring (Electric Cyan)
        if outer_alpha > 5:
            pen = QPen(QColor(0, 229, 255, outer_alpha), 2.2)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(0, 229, 255, int(outer_alpha * 0.15))))
            painter.drawEllipse(
                int(center_x - outer_radius),
                int(center_y - outer_radius),
                int(outer_radius * 2),
                int(outer_radius * 2)
            )

        # 2. Secondary Harmonic Ring (Cyber Violet)
        secondary_cycle = ((self.phase + math.pi) % (2 * math.pi)) / (2 * math.pi)
        sec_radius = 8.0 + secondary_cycle * (max_radius - 8.0)
        sec_alpha = int(180 * (1.0 - secondary_cycle) * self.fade_alpha)
        if sec_alpha > 5:
            sec_pen = QPen(QColor(168, 85, 247, sec_alpha), 1.6)
            painter.setPen(sec_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(
                int(center_x - sec_radius),
                int(center_y - sec_radius),
                int(sec_radius * 2),
                int(sec_radius * 2)
            )

        # 3. Inner Static Target Reticle (High-Contrast Neon Dot)
        core_alpha = int(255 * self.fade_alpha)
        if core_alpha > 10:
            core_pen = QPen(QColor(255, 255, 255, core_alpha), 1.5)
            painter.setPen(core_pen)
            painter.setBrush(QBrush(QColor(0, 229, 255, core_alpha)))
            painter.drawEllipse(int(center_x - 5), int(center_y - 5), 10, 10)

            # Tiny Crosshairs
            ch_pen = QPen(QColor(0, 229, 255, int(200 * self.fade_alpha)), 1.2)
            painter.setPen(ch_pen)
            painter.drawLine(int(center_x - 12), int(center_y), int(center_x - 6), int(center_y))
            painter.drawLine(int(center_x + 6), int(center_y), int(center_x + 12), int(center_y))
            painter.drawLine(int(center_x), int(center_y - 12), int(center_x), int(center_y - 6))
            painter.drawLine(int(center_x), int(center_y + 6), int(center_x), int(center_y + 12))


_ACTIVE_BEACONS = []


def show_visual_beacon(screen_x: int, screen_y: int, duration: float = 1.5) -> Optional[CursorTargetBeacon]:
    """
    Convenience function to instantiate and trigger an on-screen target beacon.
    Safe to invoke when a QApplication event loop is active.
    """
    app = QApplication.instance()
    if app is None:
        return None

    beacon = CursorTargetBeacon(size=84)
    _ACTIVE_BEACONS.append(beacon)

    # Clean up reference when closed
    beacon.destroyed.connect(lambda: _ACTIVE_BEACONS.remove(beacon) if beacon in _ACTIVE_BEACONS else None)
    beacon.trigger_at(screen_x, screen_y, duration)
    return beacon
