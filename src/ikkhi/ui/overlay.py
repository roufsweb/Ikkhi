"""
Floating Companion HUD Overlay for Ikkhi Desktop Assistant.
Delivers a frameless, translucent, non-intrusive status pill with reactive audio waveforms.
"""

import math
from typing import Optional
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QFont, QPaintEvent
from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QProgressBar
)
from ikkhi.ui.theme import DARK_THEME_QSS


class AudioWaveformVisualizer(QWidget):
    """
    Renders an organic, multi-bar audio waveform that dynamically fluctuates
    in proportion to incoming microphone RMS amplitude.
    """

    def __init__(self, parent: Optional[QWidget] = None, bar_count: int = 5) -> None:
        super().__init__(parent)
        self.bar_count = bar_count
        self.current_rms = 0.0
        self.target_rms = 0.0
        self.phase = 0.0
        self.setFixedSize(54, 28)

        # Smooth animation interpolation timer (40 FPS)
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._step_animation)
        self._anim_timer.start(25)

    def set_rms(self, rms_val: float) -> None:
        """Update target RMS amplitude (normalized between 0.0 and 1.0)."""
        self.target_rms = max(0.0, min(1.0, rms_val))

    def _step_animation(self) -> None:
        """Smoothly interpolate current RMS toward target and advance wave phase."""
        self.current_rms += (self.target_rms - self.current_rms) * 0.35
        self.phase = (self.phase + 0.18) % (2 * math.pi)
        self.update()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_w = 4.0
        spacing = 5.0
        total_bars_w = self.bar_count * bar_w + (self.bar_count - 1) * spacing
        start_x = (w - total_bars_w) / 2.0
        center_y = h / 2.0

        for i in range(self.bar_count):
            # Center-weighted harmonic bell curve for natural voice formant distribution
            center_idx = (self.bar_count - 1) / 2.0
            dist = abs(i - center_idx)
            bell_weight = max(0.45, 1.0 - (dist / (center_idx + 1.0)) ** 1.3)

            harmonic = (math.sin(self.phase + i * 1.05) * 0.35 + 0.65) * bell_weight
            amp = max(0.12, self.current_rms * harmonic)
            bar_h = max(4.0, amp * (h - 6))

            x = start_x + i * (bar_w + spacing)
            y = center_y - (bar_h / 2.0)

            # Gradient from electric cyan to vibrant violet
            grad = QLinearGradient(x, y, x, y + bar_h)
            grad.setColorAt(0.0, QColor(0, 229, 255, 240))
            grad.setColorAt(1.0, QColor(168, 85, 247, 240))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(int(x), int(y), int(bar_w), int(bar_h), 2.0, 2.0)


class FloatingCompanionOverlay(QWidget):
    """
    Translucent, frameless, always-on-top companion HUD pill widget.
    Configured as a Tool window to prevent stealing focus from active creative software.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._drag_position = QPoint()
        self._current_state = "idle"

        self._init_window_flags()
        self._init_ui()
        self._init_timers()

        self.setStyleSheet(DARK_THEME_QSS)

    def _init_window_flags(self) -> None:
        """Configure non-intrusive stay-on-top window attributes."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setMinimumWidth(280)
        self.setFixedHeight(54)

    def _init_ui(self) -> None:
        """Assemble the visual hierarchy of the HUD pill."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)

        # Frosted glass container
        self.container = QFrame(self)
        self.container.setObjectName("hudContainer")
        self.container.setProperty("state", "idle")

        # Soft drop shadow glow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)

        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(14, 4, 14, 4)
        container_layout.setSpacing(10)

        # Monogram pill icon
        self.monogram_label = QLabel("ই", self.container)
        self.monogram_label.setFixedSize(26, 26)
        self.monogram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monogram_label.setStyleSheet(
            "background-color: rgba(0, 229, 255, 0.18);"
            "color: #00e5ff;"
            "border-radius: 13px;"
            "font-size: 15px;"
            "font-weight: 800;"
        )

        # Text labels stack
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)
        text_layout.setContentsMargins(0, 2, 0, 2)

        self.title_label = QLabel("Ikkhi Ready", self.container)
        self.title_label.setStyleSheet("color: #ffffff; font-weight: 700; font-size: 13px;")

        self.detail_label = QLabel("Hold Ctrl+Alt+Space", self.container)
        self.detail_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        self.detail_label.setMaximumWidth(320)

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.detail_label)

        # Context badge (Active creative application)
        self.context_badge = QLabel("Desktop", self.container)
        self.context_badge.setObjectName("contextBadge")
        self.context_badge.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.06);"
            "color: #38bdf8;"
            "border: 1px solid rgba(255, 255, 255, 0.12);"
            "border-radius: 6px;"
            "padding: 2px 7px;"
            "font-family: 'JetBrains Mono', 'Segoe UI Variable', monospace;"
            "font-size: 10px;"
            "font-weight: 600;"
        )

        # Tier feedback badge (clean, minimal indicator)
        self.tier_badge = QLabel("local", self.container)
        self.tier_badge.setObjectName("tierBadge")
        self.tier_badge.setStyleSheet(
            "background-color: rgba(16, 185, 129, 0.14);"
            "color: #34d399;"
            "border: 1px solid rgba(16, 185, 129, 0.35);"
            "border-radius: 6px;"
            "padding: 2px 7px;"
            "font-family: 'JetBrains Mono', 'Segoe UI Variable', monospace;"
            "font-size: 10px;"
            "font-weight: 700;"
        )
        self.tier_badge.setVisible(False)

        # Reactive Waveform visualizer
        self.waveform = AudioWaveformVisualizer(self.container)
        self.waveform.setVisible(False)

        # Indeterminate Progress Bar for Processing State
        self.progress_bar = QProgressBar(self.container)
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setFixedSize(50, 4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background: rgba(255,255,255,0.1); border-radius: 2px; }"
            "QProgressBar::chunk { background: #a855f7; border-radius: 2px; }"
        )
        self.progress_bar.setVisible(False)

        container_layout.addWidget(self.monogram_label)
        container_layout.addLayout(text_layout)
        container_layout.addWidget(self.context_badge)
        container_layout.addWidget(self.tier_badge)
        container_layout.addWidget(self.waveform)
        container_layout.addWidget(self.progress_bar)

        main_layout.addWidget(self.container)

    def _init_timers(self) -> None:
        """Initialize auto-revert timer to return to idle after speech."""
        self._revert_timer = QTimer(self)
        self._revert_timer.setSingleShot(True)
        self._revert_timer.timeout.connect(self._revert_to_idle)

    @pyqtSlot()
    def _revert_to_idle(self) -> None:
        self.set_state("idle", "Hold Ctrl+Alt+Space to speak")

    def set_active_app(self, app_name: str) -> None:
        """Dynamically ground the HUD pill with the active application name."""
        clean_name = app_name.strip() or "Desktop"
        if len(clean_name) > 20:
            clean_name = clean_name[:18] + "…"
        self.context_badge.setText(clean_name)
        self.adjustSize()

    def set_tier_feedback(self, tier_label: str) -> None:
        """Flash execution tier feedback badge."""
        if "Tier 0" in tier_label or "Local" in tier_label:
            self.tier_badge.setText("local")
            self.tier_badge.setStyleSheet(
                "background-color: rgba(16, 185, 129, 0.14); color: #34d399; "
                "border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 6px; "
                "padding: 2px 7px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700;"
            )
        else:
            self.tier_badge.setText("cloud")
            self.tier_badge.setStyleSheet(
                "background-color: rgba(168, 85, 247, 0.16); color: #c084fc; "
                "border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 6px; "
                "padding: 2px 7px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700;"
            )
        self.tier_badge.setVisible(True)
        self.adjustSize()

    def set_state(self, state: str, detail: str = "") -> None:
        """
        Transitions the companion overlay across functional operational states:
        'idle' | 'listening' | 'processing' | 'speaking'
        """
        self._current_state = state
        self.container.setProperty("state", state)
        self.container.style().unpolish(self.container)
        self.container.style().polish(self.container)

        if state == "listening":
            self._revert_timer.stop()
            self.monogram_label.setStyleSheet(
                "background-color: rgba(0, 229, 255, 0.35); color: #00e5ff; border-radius: 13px;"
            )
            self.title_label.setText("Listening...")
            self.detail_label.setText(detail or "Speak into microphone...")
            self.waveform.setVisible(True)
            self.progress_bar.setVisible(False)
            self.tier_badge.setVisible(False)

        elif state == "processing":
            self._revert_timer.stop()
            self.monogram_label.setStyleSheet(
                "background-color: rgba(168, 85, 247, 0.35); color: #c084fc; border-radius: 13px;"
            )
            self.title_label.setText("Processing...")
            self.detail_label.setText(detail or "Transcribing on CUDA...")
            self.waveform.setVisible(False)
            self.progress_bar.setVisible(True)
            self.tier_badge.setVisible(False)

        elif state == "speaking":
            self.monogram_label.setStyleSheet(
                "background-color: rgba(16, 185, 129, 0.35); color: #34d399; border-radius: 13px;"
            )
            self.title_label.setText("Speaking...")
            self.detail_label.setText(detail)
            self.waveform.setVisible(False)
            self.progress_bar.setVisible(False)
            self.tier_badge.setVisible(True)
            # Revert back to idle after 4.5 seconds
            self._revert_timer.start(4500)

        else: # idle
            self.monogram_label.setStyleSheet(
                "background-color: rgba(0, 229, 255, 0.18); color: #00e5ff; border-radius: 13px;"
            )
            self.title_label.setText("Ikkhi Ready")
            self.detail_label.setText(detail or "Say 'Hey Ikkhi' or Hold Ctrl+Alt+Space")
            self.waveform.setVisible(False)
            self.progress_bar.setVisible(False)
            self.tier_badge.setVisible(False)

        self.adjustSize()

    def update_rms(self, level: float) -> None:
        """Relay raw or scaled RMS amplitude to the waveform visualizer."""
        if self._current_state == "listening":
            self.waveform.set_rms(level)

    def mousePressEvent(self, event) -> None:
        """Capture initial cursor offset to facilitate dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        """Smoothly translate window across desktop space upon dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
