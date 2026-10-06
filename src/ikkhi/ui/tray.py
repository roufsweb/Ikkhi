"""
Windows System Tray Applet for Ikkhi Desktop Assistant.
Embeds procedural high-resolution iconography and context controls.
"""

from typing import Callable, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QLinearGradient, QAction
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QWidget


def generate_procedural_icon(size: int = 64) -> QIcon:
    """
    Synthesize an anti-aliased icon dynamically using QPainter.
    Eliminates reliance on external asset files during standalone binary distribution.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Rounded squircle background
    rect_margin = size * 0.08
    rect_size = size - (rect_margin * 2)

    bg_grad = QLinearGradient(0, 0, size, size)
    bg_grad.setColorAt(0.0, QColor(14, 20, 32))
    bg_grad.setColorAt(1.0, QColor(24, 18, 43))

    painter.setPen(QColor(0, 229, 255, 180))
    painter.setBrush(bg_grad)
    painter.drawRoundedRect(
        int(rect_margin), int(rect_margin),
        int(rect_size), int(rect_size),
        size * 0.28, size * 0.28
    )

    # Stylized glyph "ই"
    font = QFont("Segoe UI", int(size * 0.48), QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(0, 229, 255))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "ই")

    painter.end()
    return QIcon(pixmap)


class IkkhiSystemTray(QSystemTrayIcon):
    """
    System Tray controller providing background persistence, status notifications,
    and instantaneous quick-access context actions.
    """

    toggle_overlay_requested = pyqtSignal()
    open_dashboard_requested = pyqtSignal()
    toggle_mute_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setIcon(generate_procedural_icon(64))
        self.setToolTip("Ikkhi Desktop Assistant (Active)")
        self._is_muted = False

        self._build_context_menu()
        self.activated.connect(self._on_tray_activated)

    def _build_context_menu(self) -> None:
        """Construct the contextual right-click menu."""
        menu = QMenu()
        menu.setStyleSheet(
            "QMenu { background-color: #121826; color: #e2e8f0; border: 1px solid rgba(255,255,255,0.12); "
            "border-radius: 8px; padding: 6px; } "
            "QMenu::item { padding: 6px 24px; border-radius: 4px; font-size: 12px; } "
            "QMenu::item:selected { background-color: rgba(0, 229, 255, 0.2); color: #00e5ff; } "
            "QMenu::separator { height: 1px; background: rgba(255,255,255,0.08); margin: 4px 8px; }"
        )

        # Title entry
        title_action = QAction("Ikkhi Desktop Assistant", menu)
        title_action.setEnabled(False)
        menu.addAction(title_action)
        menu.addSeparator()

        # Overlay visibility toggle
        self.action_toggle_overlay = QAction("Hide Companion HUD", menu)
        self.action_toggle_overlay.triggered.connect(self.toggle_overlay_requested.emit)
        menu.addAction(self.action_toggle_overlay)

        # Settings & Analytics Dashboard
        action_dashboard = QAction("Open Control Panel & Analytics", menu)
        action_dashboard.triggered.connect(self.open_dashboard_requested.emit)
        menu.addAction(action_dashboard)

        # Mute / Unmute
        self.action_mute = QAction("Mute Microphone Hook", menu)
        self.action_mute.triggered.connect(self._handle_mute_toggle)
        menu.addAction(self.action_mute)

        menu.addSeparator()

        # Termination
        action_quit = QAction("Exit Ikkhi", menu)
        action_quit.triggered.connect(self.exit_requested.emit)
        menu.addAction(action_quit)

        self.setContextMenu(menu)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle single-click or double-click on tray icon."""
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            self.open_dashboard_requested.emit()

    def _handle_mute_toggle(self) -> None:
        self._is_muted = not self._is_muted
        self.action_mute.setText("Unmute Microphone Hook" if self._is_muted else "Mute Microphone Hook")
        self.setToolTip(f"Ikkhi Assistant ({'MUTED' if self._is_muted else 'Active'})")
        self.toggle_mute_requested.emit()

    def update_overlay_state(self, visible: bool) -> None:
        """Update toggle menu text based on actual overlay visibility."""
        self.action_toggle_overlay.setText("Hide Companion HUD" if visible else "Show Companion HUD")

    def notify(self, title: str, message: str) -> None:
        """Emit a native desktop notification bubble."""
        self.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
