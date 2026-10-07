"""
Central Logging & User Interaction Correlation Engine for Ikkhi.
Maintains persistent rotating file logs in storage/ikkhi.log and stream outputs.
Tracks hardware inputs, window changes, and their deterministic relation to Ikkhi.
"""

import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from ikkhi.core.paths import get_storage_dir

_IS_CONFIGURED = False


def setup_logging(
    storage_dir: Optional[Path] = None,
    debug: bool = True,
    log_filename: str = "ikkhi.log"
) -> logging.Logger:
    """
    Initializes root and 'ikkhi' loggers with dual output:
    1. Rotating persistent file log at storage/ikkhi.log (up to 10MB x 5 backups)
    2. Formatted Console stdout stream
    """
    global _IS_CONFIGURED

    target_dir = storage_dir or get_storage_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = target_dir / log_filename

    root_logger = logging.getLogger()
    log_level = logging.DEBUG if debug else logging.INFO
    root_logger.setLevel(log_level)

    if not _IS_CONFIGURED:
        # Standard format with millisecond timestamps
        fmt = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 1. Console Stream Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(fmt)
        root_logger.addHandler(console_handler)

        # 2. Persistent Rotating File Handler
        try:
            file_handler = RotatingFileHandler(
                filename=str(log_file_path),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG in persistent file
            file_handler.setFormatter(fmt)
            root_logger.addHandler(file_handler)
        except Exception as exc:
            print(f"[Warning] Could not initialize file logging to {log_file_path}: {exc}", file=sys.stderr)

        # Quiet overly verbose external third-party loggers
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("pynput").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)

        _IS_CONFIGURED = True

    app_logger = logging.getLogger("ikkhi")
    app_logger.info("=" * 60)
    app_logger.info("Ikkhi Logging Subsystem Initialized. Log File: %s", log_file_path)
    app_logger.info("=" * 60)
    return app_logger


def close_logging() -> None:
    """Closes and removes all root and ikkhi handlers to release locked file descriptors."""
    global _IS_CONFIGURED
    root = logging.getLogger()
    for h in list(root.handlers):
        try:
            h.flush()
            h.close()
        except Exception:
            pass
        root.removeHandler(h)
    _IS_CONFIGURED = False


def get_logger(name: str = "ikkhi") -> logging.Logger:
    """Acquire a module-specific logger under the ikkhi namespace."""
    if not _IS_CONFIGURED:
        setup_logging()
    return logging.getLogger(name)


class InputCorrelationTracker:
    """
    Logs and correlates every host user input (keys, hotkeys, active windows, audio RMS)
    in relation to Ikkhi's push-to-talk triggers, speech recognition, and action execution.
    """

    def __init__(self, logger_instance: Optional[logging.Logger] = None) -> None:
        self.logger = logger_instance or get_logger("ikkhi.input_tracker")

    def log_key_event(self, event_type: str, key_name: str, active_keys: set[str], target_hotkey: str) -> None:
        """
        Logs a hardware keyboard event and explicitly determines its relation to Ikkhi.
        """
        target_tokens = set(target_hotkey.lower().replace(" ", "").split("+"))
        is_exact_match = target_tokens.issubset(active_keys)
        is_partial_overlap = bool(active_keys.intersection(target_tokens))

        if is_exact_match:
            relation = f"[RELATION: TRIGGER_MATCH] Active keys {list(active_keys)} matched Ikkhi hotkey '{target_hotkey}'!"
        elif is_partial_overlap:
            relation = f"[RELATION: PARTIAL_HOTKEY] Active keys {list(active_keys)} overlap hotkey '{target_hotkey}', awaiting full combo"
        else:
            relation = f"[RELATION: NORMAL_TYPING] Active keys {list(active_keys)} unrelated to Ikkhi trigger"

        self.logger.debug(
            "[USER_INPUT: KEY_%s] Key: '%s' | Held: %s | %s",
            event_type.upper(),
            key_name,
            sorted(list(active_keys)),
            relation
        )

    def log_window_change(self, old_window: str, new_window: str) -> None:
        """Logs active foreground window transitions across Windows."""
        self.logger.info(
            "[USER_CONTEXT: WINDOW_FOCUS] Switched active window: '%s' -> '%s'",
            old_window,
            new_window
        )

    def log_audio_capture(self, state: str, device_info: str, rms_level: float, duration_s: float = 0.0) -> None:
        """Logs audio hardware capture status, RMS energy levels, and duration."""
        if state == "START":
            self.logger.info(
                "[IKKHI_AUDIO: START] Recording started on '%s' | Initial RMS: %.6f",
                device_info,
                rms_level
            )
        elif state == "STOP":
            energy_desc = "Silent/Near-zero (check mic selection!)" if rms_level < 0.0005 else f"Audible (RMS: {rms_level:.5f})"
            self.logger.info(
                "[IKKHI_AUDIO: STOP] Recording finished | Duration: %.2fs | Final RMS: %.6f (%s)",
                duration_s,
                rms_level,
                energy_desc
            )

    def log_transcription(self, transcript: str, duration_s: float, model: str) -> None:
        """Logs speech-to-text inference result."""
        clean = transcript.strip()
        if clean:
            self.logger.info(
                "[IKKHI_STT: SUCCESS] Transcribed: \"%s\" in %.3fs via %s",
                clean,
                duration_s,
                model
            )
        else:
            self.logger.warning(
                "[IKKHI_STT: EMPTY] No spoken words detected in %.3fs audio buffer via %s",
                duration_s,
                model
            )

    def log_action_execution(self, command: str, tier: str, result: str, execution_time_s: float) -> None:
        """Logs action router resolution and execution status."""
        self.logger.info(
            "[IKKHI_ACTION: EXECUTED] Command: \"%s\" | Tier: %s | Elapsed: %.3fs | Result: %s",
            command,
            tier,
            execution_time_s,
            result
        )
