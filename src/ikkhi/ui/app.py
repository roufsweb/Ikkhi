"""
Master Graphical Application Coordinator for Ikkhi Desktop Assistant.
Integrates the HUD Overlay, System Tray, Analytics Dashboard, and Asynchronous Controller.
"""

import sys
import logging
from typing import Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication

from ikkhi.core.config import AppConfig
from ikkhi.ui.theme import DARK_THEME_QSS
from ikkhi.ui.overlay import FloatingCompanionOverlay
from ikkhi.ui.tray import IkkhiSystemTray
from ikkhi.ui.dashboard import DashboardWindow
from ikkhi.ui.controller import GUIController

logger = logging.getLogger("ikkhi.ui.app")


class IkkhiApplication:
    """
    Encapsulates the lifecycle, window positioning, and inter-component signal wiring
    for the Ikkhi Desktop GUI environment.
    """

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or AppConfig.load_from_yaml("config.yaml")

        # Initialize Qt Application instance if not already running
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.app.setApplicationName("Ikkhi")
        self.app.setApplicationDisplayName("Ikkhi Desktop Assistant")
        self.app.setStyleSheet(DARK_THEME_QSS)

        # Instantiate core UI subsystems
        self.controller = GUIController(self.config)
        self.overlay = FloatingCompanionOverlay()
        self.tray = IkkhiSystemTray()
        self.dashboard = DashboardWindow(self.config)

        self._wire_signals()
        self._position_overlay()

    def _wire_signals(self) -> None:
        """Establish type-safe signal/slot bindings across UI subsystems."""
        # Controller -> Overlay
        self.controller.state_changed.connect(self.overlay.set_state)
        self.controller.rms_updated.connect(self.overlay.update_rms)

        # Controller -> Dashboard History & Metrics
        self.controller.command_logged.connect(self.dashboard.log_command)

        # System Tray -> Actions
        self.tray.toggle_overlay_requested.connect(self._toggle_overlay)
        self.tray.open_dashboard_requested.connect(self._show_dashboard)
        self.tray.toggle_mute_requested.connect(self._toggle_mute)
        self.tray.exit_requested.connect(self.shutdown)

    def _position_overlay(self) -> None:
        """Position the companion HUD gracefully at the top-center of the primary display."""
        primary_screen = QGuiApplication.primaryScreen()
        if primary_screen:
            geom = primary_screen.availableGeometry()
            overlay_w = self.overlay.width()
            pos_x = geom.x() + (geom.width() - overlay_w) // 2
            pos_y = geom.y() + 45  # 45px padding from screen summit
            self.overlay.move(pos_x, pos_y)

    def _toggle_overlay(self) -> None:
        is_vis = self.overlay.isVisible()
        self.overlay.setVisible(not is_vis)
        self.tray.update_overlay_state(not is_vis)

    def _show_dashboard(self) -> None:
        self.dashboard.show()
        self.dashboard.activateWindow()
        self.dashboard.raise_()

    def _toggle_mute(self) -> None:
        new_mute = not self.controller._is_muted
        self.controller.set_muted(new_mute)

    def start(self) -> None:
        """Launch visual presentation and commence background hotkey monitoring."""
        self.overlay.show()
        self.tray.show()
        self.controller.start_listeners()

        self.tray.notify(
            "Ikkhi Assistant Online",
            f"Push-to-Talk active: [{self.config.audio.push_to_talk_key.upper()}]. Ready for commands."
        )

    def shutdown(self) -> None:
        """Gracefully release hardware listeners and terminate application."""
        logger.info("Initiating graceful shutdown of Ikkhi GUI...")
        self.controller.stop_listeners()
        self.overlay.close()
        self.dashboard.close()
        self.tray.hide()
        self.app.quit()


def launch_gui(config: Optional[AppConfig] = None) -> int:
    """Entry point for executing the standalone Ikkhi GUI application."""
    ikkhi_app = IkkhiApplication(config)
    ikkhi_app.start()
    return ikkhi_app.app.exec()
