"""
Local Text-to-Speech (TTS) Synthesis Subsystem.
Provides 100% offline, zero-token voice feedback to emulate HeyClicky without cloud costs.
"""

import threading
import queue
import logging
import ctypes
from typing import Optional
from ikkhi.core.config import AudioSettings

logger = logging.getLogger(__name__)


class LocalSpeechEngine:
    """Manages asynchronous, local neural and SAPI voice synthesis with 0 cloud credits."""

    def __init__(self, settings: AudioSettings) -> None:
        self.settings = settings
        self._queue: queue.Queue[str] = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._init_worker()

    def _init_worker(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._speech_worker, daemon=True, name="IkkhiSpeechWorker")
        self._thread.start()

    def speak(self, text: str, wait: bool = False) -> None:
        """Enqueues text for asynchronous spoken synthesis."""
        clean_text = text.strip()
        if not clean_text:
            return

        if wait:
            self._synthesize(clean_text)
        else:
            self._queue.put(clean_text)

    def _speech_worker(self) -> None:
        """Worker loop processing spoken text from the queue."""
        # Initialize COM on this worker thread for Windows SAPI
        try:
            ctypes.windll.ole32.CoInitialize(None)
        except Exception:
            pass

        while self._running:
            try:
                text = self._queue.get(timeout=0.5)
                self._synthesize(text)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as exc:
                logger.error("Error in speech worker: %s", exc)

    def _synthesize(self, text: str) -> None:
        """Synthesizes text locally using Windows native SAPI / COM interface."""
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        except Exception:
            # Fallback to PowerShell System.Speech if pywin32 is not initialized
            import subprocess
            clean_safe = text.replace('"', '""').replace("'", "''")
            cmd = f'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak("{clean_safe}")'
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd], capture_output=True)

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
