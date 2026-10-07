"""
Unit tests for the centralized logging subsystem and InputCorrelationTracker.
"""

import tempfile
from pathlib import Path
from ikkhi.core.logger import setup_logging, InputCorrelationTracker, get_logger


def test_setup_logging_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        logger = setup_logging(storage_dir=tmp_path, debug=True, log_filename="test_ikkhi.log")
        logger.info("Test log line written successfully.")

        log_file = tmp_path / "test_ikkhi.log"
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "Test log line written successfully." in content
        from ikkhi.core.logger import close_logging
        close_logging()


def test_input_correlation_tracker_key_events():
    tracker = InputCorrelationTracker()
    # Test hotkey matching logic
    target_hotkey = "ctrl+alt+space"

    # Exact match
    tracker.log_key_event("press", "space", {"ctrl", "alt", "space"}, target_hotkey)

    # Partial match
    tracker.log_key_event("press", "ctrl", {"ctrl"}, target_hotkey)

    # Unrelated key
    tracker.log_key_event("press", "a", {"a"}, target_hotkey)


def test_input_correlation_tracker_context_events():
    tracker = InputCorrelationTracker()
    tracker.log_window_change("Desktop", "VS Code")
    tracker.log_audio_capture("START", "Realtek Mic", 0.01)
    tracker.log_audio_capture("STOP", "Realtek Mic", 0.05, 2.5)
    tracker.log_transcription("increase volume", 0.25, "faster-whisper [base.en]")
    tracker.log_action_execution("increase volume", "Tier 0", "Increased volume by 10%", 0.05)
