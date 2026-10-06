"""
Graphical User Interface and companion desktop subsystem for Ikkhi.
"""

from ikkhi.ui.app import IkkhiApplication, launch_gui
from ikkhi.ui.overlay import FloatingCompanionOverlay
from ikkhi.ui.tray import IkkhiSystemTray
from ikkhi.ui.dashboard import DashboardWindow

__all__ = [
    "IkkhiApplication",
    "launch_gui",
    "FloatingCompanionOverlay",
    "IkkhiSystemTray",
    "DashboardWindow",
]
