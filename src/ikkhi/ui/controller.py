"""
Asynchronous Controller & Worker Pipeline for Ikkhi Desktop GUI.
Bridges Push-to-Talk events, audio capture, Whisper CUDA inference, and UI state signals.
"""

import time
import logging
import numpy as np
from datetime import datetime
from typing import Optional
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

from ikkhi.core.config import AppConfig
from ikkhi.core.orchestrator import IkkhiOrchestrator
from ikkhi.audio.capture import AudioCaptureEngine
from ikkhi.audio.stt import WhisperSTTEngine
from ikkhi.audio.hotkey import PushToTalkListener

logger = logging.getLogger("ikkhi.ui.controller")


class AudioInferenceWorker(QThread):
    """
    Background worker thread executing Whisper GPU transcription and orchestrator dispatch.
    Ensures the GUI event loop maintains an uncompromised 60 FPS without frame drops.
    """

    inference_completed = pyqtSignal(str, str, str)  # (transcript, tier, response)
    inference_failed = pyqtSignal(str)              # (error_message)

    def __init__(self, stt_engine: WhisperSTTEngine, orchestrator: IkkhiOrchestrator, audio: np.ndarray) -> None:
        super().__init__()
        self.stt_engine = stt_engine
        self.orchestrator = orchestrator
        self.audio = audio

    def run(self) -> None:
        try:
            transcript, _ = self.stt_engine.transcribe(self.audio)
            transcript_clean = transcript.strip()
            if not transcript_clean:
                self.inference_failed.emit("No audible speech detected")
                return

            # Determine routing classification preview
            intent = self.orchestrator.router.classify_intent(transcript_clean)
            tier_name = "Tier 0 (Local Deterministic)" if intent.tier == 0 else "Tier 1 (Cloud Multimodal)"

            # Execute intent via orchestrator
            response = self.orchestrator.process_transcript(transcript_clean)
            self.inference_completed.emit(transcript_clean, tier_name, response)
        except Exception as exc:
            logger.error("Inference worker encountered an error: %s", exc)
            self.inference_failed.emit(str(exc))


class GUIController(QObject):
    """
    Primary orchestrator for the graphical interface, coordinating hardware listeners,
    visual overlays, tray notifications, and background inference tasks.
    """

    # Signals consumed by GUI widgets (Overlay & Dashboard)
    state_changed = pyqtSignal(str, str)              # (state_name, detail_text)
    rms_updated = pyqtSignal(float)                   # (normalized_rms_0_to_1)
    command_logged = pyqtSignal(str, str, str, str)   # (timestamp, utterance, tier, response)

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.orchestrator = IkkhiOrchestrator(config)
        self.capture_engine = AudioCaptureEngine(config.audio)
        self.stt_engine = WhisperSTTEngine(config.audio, config.network)
        
        self._is_muted = False
        self._active_worker: Optional[AudioInferenceWorker] = None

        # Setup Push-to-Talk global keyboard listener
        self.hotkey_listener = PushToTalkListener(
            settings=config.audio,
            on_start=self._on_hotkey_pressed,
            on_stop=self._on_hotkey_released
        )

    def start_listeners(self) -> None:
        """Commence background keyboard hooks and warm up Whisper STT."""
        try:
            self.hotkey_listener.start()
            logger.info("Global Push-to-Talk hook started successfully.")
        except Exception as exc:
            logger.warning("Could not hook global hotkey: %s", exc)

        # Pre-warm local Whisper model
        try:
            self.stt_engine.load_model()
        except Exception as exc:
            logger.warning("Whisper pre-warm deferred: %s", exc)

    def stop_listeners(self) -> None:
        """Safely release audio resources and terminate keyboard hooks."""
        try:
            self.hotkey_listener.stop()
        except Exception:
            pass
        self.capture_engine.close()
        self.orchestrator.speech_engine.stop()

    def set_muted(self, muted: bool) -> None:
        """Toggle microphone mute status."""
        self._is_muted = muted
        if muted:
            self.state_changed.emit("idle", "Microphone Hook Muted")
        else:
            self.state_changed.emit("idle", "Hold Ctrl+Alt+Space to speak")

    def _on_hotkey_pressed(self) -> None:
        if self._is_muted:
            return

        self.state_changed.emit("listening", "Listening to microphone...")
        self.capture_engine.start_recording()

        # Monitor RMS in audio stream periodically
        # Relay simulated or capture RMS
        rms = self.capture_engine.get_live_rms()
        self.rms_updated.emit(min(1.0, rms * 15.0))

    def _on_hotkey_released(self) -> None:
        if self._is_muted:
            return

        self.state_changed.emit("processing", "Transcribing speech on CUDA...")
        audio_buffer = self.capture_engine.stop_recording()

        if len(audio_buffer) == 0:
            self.state_changed.emit("idle", "No audio recorded")
            return

        # Dispatch inference to dedicated QThread to prevent GUI lag
        self._active_worker = AudioInferenceWorker(self.stt_engine, self.orchestrator, audio_buffer)
        self._active_worker.inference_completed.connect(self._handle_inference_success)
        self._active_worker.inference_failed.connect(self._handle_inference_failure)
        self._active_worker.start()

    @pyqtSlot(str, str, str)
    def _handle_inference_success(self, transcript: str, tier: str, response: str) -> None:
        now_str = datetime.now().strftime("%H:%M:%S")
        self.state_changed.emit("speaking", f'"{transcript}" → {response}')
        self.command_logged.emit(now_str, transcript, tier, response)

    @pyqtSlot(str)
    def _handle_inference_failure(self, error_msg: str) -> None:
        self.state_changed.emit("idle", f"Notice: {error_msg}")

    def execute_simulated_command(self, command_text: str) -> str:
        """Simulate programmatic voice command execution for automated diagnostics."""
        now_str = datetime.now().strftime("%H:%M:%S")
        intent = self.orchestrator.router.classify_intent(command_text)
        tier_name = "Tier 0 (Local Deterministic)" if intent.tier == 0 else "Tier 1 (Cloud Multimodal)"

        self.state_changed.emit("processing", f"Executing: {command_text}")
        response = self.orchestrator.process_transcript(command_text)
        self.state_changed.emit("speaking", response)
        self.command_logged.emit(now_str, command_text, tier_name, response)
        return response
