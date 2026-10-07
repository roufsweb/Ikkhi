"""
Wake-Word Detection Engine for Ikkhi.
Listens continuously for trigger phrases ("hey ikkhi", "hey ikki", "hey siri", "hey google", "jarvis", etc.)
utilizing dynamic ambient noise calibration and fast CUDA transcription with <1% CPU footprint.
"""

import time
import queue
import logging
import threading
from typing import Optional, Callable, List
import numpy as np
import sounddevice as sd

from ikkhi.core.config import AudioSettings
from ikkhi.audio.stt import WhisperSTTEngine
from ikkhi.audio.capture import resolve_optimal_input_device

logger = logging.getLogger("ikkhi.audio.wakeword")


class WakeWordListener:
    """
    Low-overhead background audio stream processor that continuously scans
    incoming microphone frames for activation wake words.
    """

    # Extended phonetic variations and common assistant triggers for natural invocation
    WAKE_KEYWORDS = [
        "hey ikkhi", "hey ikki", "hey eki", "hey iki", "hey ikhi",
        "hey iggy", "hey itchy", "hey cookie", "hey key", "hey, ikkhi", "hey, ikki",
        "ikkhi", "ikki", "ickey", "iki", "ikhi", "hi ikkhi", "hi ikki",
        "hey assistant", "assistant", "hey siri", "hey google", "hey jarvis", "jarvis", "computer"
    ]

    def __init__(
        self,
        settings: AudioSettings,
        on_wake: Callable[[str, Optional[str]], None],  # on_wake(trigger_name, optional_command)
        stt_engine: Optional[WhisperSTTEngine] = None,
        threshold: float = 0.5,
    ) -> None:
        self.settings = settings
        self.sample_rate = settings.sample_rate  # 16000 Hz
        self.on_wake = on_wake
        self.stt_engine = stt_engine
        self.threshold = threshold
        self.target_phrase = settings.wake_word.lower().strip()  # "hey ikkhi"

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=200)
        self._stream: Optional[sd.InputStream] = None

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Real-time audio callback collecting 16kHz mono chunks."""
        if not self._running:
            return
        chunk = indata[:, 0].copy()
        try:
            self._audio_queue.put_nowait(chunk)
        except queue.Full:
            pass

    def start(self) -> None:
        """Initiate background audio stream and inference worker thread."""
        if self._running:
            return

        self._running = True
        dev_idx = resolve_optimal_input_device(getattr(self.settings, "input_device", None))

        # Block size of 1280 samples = 80ms at 16kHz
        try:
            self._stream = sd.InputStream(
                device=dev_idx,
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16",
                blocksize=1280,
                callback=self._audio_callback
            )
            self._stream.start()
        except Exception as exc:
            logger.error("Failed to start wake-word audio stream: %s", exc)
            self._running = False
            return

        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="Ikkhi-WakeWord-Thread")
        self._thread.start()
        logger.info("WakeWordListener activated on device [%s] for phrases: %s", dev_idx, self.WAKE_KEYWORDS[:4])

    def stop(self) -> None:
        """Cleanly terminate worker and physical input audio stream."""
        self._running = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            self._thread = None
        logger.info("WakeWordListener stopped.")

    def _worker_loop(self) -> None:
        """Inference loop consuming chunks and evaluating wake models."""
        speech_buffer: List[np.ndarray] = []
        silence_chunks = 0
        is_in_speech = False
        cooldown_until = 0.0

        # Dynamic noise floor calibration
        noise_samples: List[float] = []
        noise_floor = 120.0

        while self._running:
            try:
                chunk = self._audio_queue.get(timeout=0.15)
            except queue.Empty:
                continue

            now = time.time()
            if now < cooldown_until:
                speech_buffer.clear()
                continue

            rms = float(np.sqrt(np.mean(np.square(chunk.astype(np.float32)))))

            # Calibrate initial background noise
            if len(noise_samples) < 15:
                noise_samples.append(rms)
                if len(noise_samples) == 15:
                    noise_floor = max(80.0, float(np.mean(noise_samples)) * 1.6)
                    logger.debug("WakeWord noise floor calibrated to: %.2f", noise_floor)
                continue

            speech_trigger = noise_floor

            if rms >= speech_trigger:
                # Active speech chunk
                is_in_speech = True
                silence_chunks = 0
                speech_buffer.append(chunk)
                # Keep buffer capped to 4 seconds maximum (50 chunks x 80ms)
                if len(speech_buffer) > 50:
                    speech_buffer.pop(0)
            else:
                # Silence chunk
                if is_in_speech:
                    silence_chunks += 1
                    speech_buffer.append(chunk)

                    # Trigger evaluation after ~240ms of trailing silence (3 chunks) and at least ~320ms of speech (4 chunks)
                    if silence_chunks >= 3 and len(speech_buffer) >= 4:
                        is_in_speech = False
                        silence_chunks = 0

                        if self.stt_engine is not None:
                            full_int16 = np.concatenate(speech_buffer, axis=0)
                            float32_audio = full_int16.astype(np.float32) / 32768.0
                            speech_buffer.clear()

                            try:
                                transcript, _ = self.stt_engine.transcribe(float32_audio)
                                clean = transcript.lower().strip()
                                if clean:
                                    logger.debug("Ambient mic heard: '%s'", clean)

                                # Check against all phonetic variations of wake triggers
                                matched_kw = None
                                for kw in self.WAKE_KEYWORDS:
                                    if kw in clean:
                                        matched_kw = kw
                                        break

                                if matched_kw:
                                    logger.info("Wake-word matched: '%s' in transcript: '%s'", matched_kw, clean)
                                    cooldown_until = now + 2.5
                                    # Extract remainder command if uttered in same sentence
                                    remainder = clean.split(matched_kw, 1)[-1].strip(" ,.!?")
                                    self.on_wake(matched_kw, remainder if remainder else None)
                            except Exception as exc:
                                logger.debug("Wake verification transcribe error: %s", exc)
                        else:
                            speech_buffer.clear()
                else:
                    speech_buffer.clear()

    def trigger_manual(self, phrase: str = "hey ikkhi") -> None:
        """Programmatic trigger for simulation and automated testing."""
        logger.info("Manual wake word triggered: '%s'", phrase)
        self.on_wake(phrase, None)
