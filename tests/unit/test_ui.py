"""
Unit test suite for Ikkhi Desktop GUI components and path resolution mechanisms.
"""

import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from ikkhi.core.config import AppConfig
from ikkhi.core.paths import (
    is_frozen, get_bundle_dir, get_storage_dir, get_profiles_dir, resolve_config_path
)
from ikkhi.ui.theme import DARK_THEME_QSS
from ikkhi.ui.tray import generate_procedural_icon
from ikkhi.ui.overlay import FloatingCompanionOverlay, AudioWaveformVisualizer
from ikkhi.ui.dashboard import DashboardWindow, MetricCard


@pytest.fixture(scope="session")
def qapp():
    """Ensure a singleton QApplication exists for GUI widget instantiations."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_path_resolution_mechanisms():
    """Verify runtime and storage path resolutions."""
    assert isinstance(is_frozen(), bool)
    bundle_dir = get_bundle_dir()
    assert bundle_dir.exists()

    storage_dir = get_storage_dir()
    assert storage_dir.exists()

    profiles_dir = get_profiles_dir()
    assert profiles_dir.exists()
    assert profiles_dir.is_relative_to(storage_dir)

    cfg_path = resolve_config_path("config.yaml")
    assert isinstance(cfg_path, Path)


def test_theme_stylesheet_contains_tokens():
    """Ensure essential dark theme QSS tokens are defined."""
    assert "background-color: #07090e;" in DARK_THEME_QSS
    assert "#00e5ff" in DARK_THEME_QSS
    assert "hudContainer" in DARK_THEME_QSS


def test_procedural_icon_generation(qapp):
    """Validate procedural vector synthesis of the tray icon."""
    icon = generate_procedural_icon(48)
    assert not icon.isNull()
    pixmap = icon.pixmap(48, 48)
    assert not pixmap.isNull()
    assert pixmap.width() == 48
    assert pixmap.height() == 48


def test_waveform_visualizer_amplitude(qapp):
    """Verify RMS amplitude bounds in waveform visualizer."""
    waveform = AudioWaveformVisualizer(None, bar_count=5)
    waveform.set_rms(0.65)
    assert waveform.target_rms == 0.65
    waveform.set_rms(1.5)  # Out of range test
    assert waveform.target_rms == 1.0
    waveform.set_rms(-0.2)
    assert waveform.target_rms == 0.0


def test_companion_overlay_states(qapp):
    """Verify state transitions and label reflections in the companion HUD overlay."""
    overlay = FloatingCompanionOverlay()
    assert overlay.windowFlags() & Qt.WindowType.FramelessWindowHint
    assert overlay.windowFlags() & Qt.WindowType.WindowStaysOnTopHint

    # Idle State
    overlay.set_state("idle", "Hold Ctrl+Alt+Space")
    assert overlay.title_label.text() == "Ikkhi Ready"
    assert overlay.waveform.isHidden()

    # Listening State
    overlay.set_state("listening", "Capturing speech...")
    assert overlay.title_label.text() == "Listening..."
    assert not overlay.waveform.isHidden()

    # Processing State
    overlay.set_state("processing", "Transcribing on CUDA...")
    assert overlay.title_label.text() == "Processing..."
    assert not overlay.progress_bar.isHidden()

    # Speaking State
    overlay.set_state("speaking", "Spoken response")
    assert overlay.title_label.text() == "Speaking..."
    assert overlay.detail_label.text() == "Spoken response"

    overlay.close()


def test_dashboard_metrics_and_logging(qapp):
    """Verify dashboard metrics calculation upon logging commands."""
    config = AppConfig()
    dashboard = DashboardWindow(config)

    # Initial metrics
    assert dashboard.stats["fast_path_count"] == 0
    assert dashboard.stats["tokens_saved"] == 0

    # Log a Tier 0 command
    dashboard.log_command("18:15:00", "increase volume", "Tier 0 (Local Fast-Path)", "Volume increased")
    assert dashboard.stats["fast_path_count"] == 1
    assert dashboard.stats["tokens_saved"] == 1800
    assert dashboard.history_table.rowCount() == 1

    # Log a Tier 1 command
    dashboard.log_command("18:15:05", "click cut button", "Tier 1 (Cloud Gemini)", "Clicked at (450, 320)")
    assert dashboard.stats["cloud_count"] == 1
    assert dashboard.history_table.rowCount() == 2

    # Verify new settings tab fields
    assert hasattr(dashboard, "input_wakeword")
    assert hasattr(dashboard, "input_project_id")
    assert dashboard.input_wakeword.text() == config.audio.wake_word
    assert dashboard.input_project_id.text() == config.ai_tier.gemini_project_id

    dashboard.close()
