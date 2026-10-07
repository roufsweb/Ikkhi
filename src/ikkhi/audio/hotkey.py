"""
Global Asynchronous Push-to-Talk Hotkey Subsystem.
Hooks hardware keyboard interrupts across Windows with 0.0% idle CPU overhead.
Correlates every user key action with Ikkhi's activation state.
"""

import threading
import logging
from typing import Callable, Optional, Set
from pynput import keyboard
from ikkhi.core.config import AudioSettings
from ikkhi.core.logger import InputCorrelationTracker

logger = logging.getLogger("ikkhi.audio.hotkey")


class PushToTalkListener:
    """Monitors global hardware key states and dispatches atomic recording triggers."""

    def __init__(
        self,
        settings: AudioSettings,
        on_start: Optional[Callable[[], None]] = None,
        on_stop: Optional[Callable[[], None]] = None,
        tracker: Optional[InputCorrelationTracker] = None
    ) -> None:
        self.settings = settings
        self.on_start = on_start
        self.on_stop = on_stop
        self._current_keys: Set[keyboard.Key | keyboard.KeyCode] = set()
        self._is_active = False
        self._listener: Optional[keyboard.Listener] = None
        self._running = False
        self._lock = threading.Lock()
        self.tracker = tracker or InputCorrelationTracker(logger)

    def _normalize_key(self, key: keyboard.Key | keyboard.KeyCode) -> str:
        """Converts pynput key representation to normalized lowercase token."""
        if isinstance(key, keyboard.Key):
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                return "ctrl"
            if key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                return "alt"
            if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
                return "shift"
            if key == keyboard.Key.space:
                return "space"
            return key.name.lower()
        elif hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key).lower()

    def _check_hotkey_match(self) -> bool:
        """Evaluates whether all components of the target hotkey are concurrently depressed."""
        target_tokens = set(self.settings.push_to_talk_key.lower().replace(" ", "").split("+"))
        active_tokens = {self._normalize_key(k) for k in self._current_keys}
        return target_tokens.issubset(active_tokens)

    def _on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            self._current_keys.add(key)
            norm_key = self._normalize_key(key)
            active_tokens = {self._normalize_key(k) for k in self._current_keys}
            
            # Log hardware input and its relation to Ikkhi
            self.tracker.log_key_event("press", norm_key, active_tokens, self.settings.push_to_talk_key)

            if not self._is_active and self._check_hotkey_match():
                self._is_active = True
                logger.info("Push-to-Talk hotkey matched: recording initiated.")
                if self.on_start:
                    try:
                        self.on_start()
                    except Exception as exc:
                        logger.error("Error in on_start callback: %s", exc)

    def _on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        with self._lock:
            norm_key = self._normalize_key(key)
            active_tokens = {self._normalize_key(k) for k in self._current_keys}
            self.tracker.log_key_event("release", norm_key, active_tokens, self.settings.push_to_talk_key)

            if self._is_active and not self._check_hotkey_match():
                self._is_active = False
                logger.info("Push-to-Talk hotkey released: recording finalized.")
                if self.on_stop:
                    try:
                        self.on_stop()
                    except Exception as exc:
                        logger.error("Error in on_stop callback: %s", exc)
            self._current_keys.discard(key)

    def start(self) -> None:
        """Starts the low-level Windows keyboard hook in a background thread."""
        if self._listener is not None:
            return
        self._running = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self._listener.daemon = True
        self._listener.start()
        logger.info("Push-to-Talk listener activated for trigger: '%s'", self.settings.push_to_talk_key)

    def stop(self) -> None:
        """Detaches the keyboard hook cleanly."""
        self._running = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
