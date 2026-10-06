"""
Wake-Word Detection Engine for Ikkhi.
Listens continuously for trigger phrases ("hey ikkhi", "ikkhi", etc.)
utilizing openWakeWord ONNX models and acoustic speech activity detection with <1% CPU footprint.
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

logger = logging.getLogger(__name__)


class WakeWordListener:
    """
    Low-overhead background audio stream processor that continuously scans
    incoming microphone frames for activation wake words.
    """

    def __init__(
        self,
        settings: AudioSettings,
        on_wake: Callable[[str, Optional[str]], None], # on_wake(trigger_name, optional_command)
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
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=150)
        self._stream: Optional[sd.InputStream] = None
        self._oww_model = None

        self._init_oww_models()

    def _init_oww_models(self) -> None:
        """Initialize openWakeWord ONNX models if available."""
        try:
            import openwakeword
            from openwakeword.model import Model

            model_paths = [
                p for p in openwakeword.get_pretrained_model_paths()
                if p.endswith(".onnx")
            ]
            if model_paths:
                self._oww_model = Model(
                    wakeword_models=model_paths,
                    inference_framework="onnx"
                )
                logger.info("Loaded openWakeWord ONNX models: %s", list(self._oww_model.models.keys()))
        except Exception as exc:
            logger.debug("openWakeWord ONNX initialization: %s", exc)
            self._oww_model = None

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
        # Block size of 1280 samples = 80ms at 16kHz
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=1280,
            callback=self._audio_callback
        )
        self._stream.start()

        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="Ikkhi-WakeWord-Thread")
        self._thread.start()
        logger.info("WakeWordListener activated for phrase: '%s'", self.target_phrase)

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
        silence_threshold = 350.0  # Amplitude threshold for int16
        silence_chunks = 0
        is_in_speech = False
        cooldown_until = 0.0

        while self._running:
            try:
                chunk = self._audio_queue.get(timeout=0.15)
            except queue.Empty:
                continue

            now = time.time()
            if now < cooldown_until:
                speech_buffer.clear()
                continue

            # 1. Quick openWakeWord check
            if self._oww_model is not None:
                try:
                    preds = self._oww_model.predict(chunk)
                    for model_name, score in preds.items():
                        if score >= self.threshold:
                            logger.info("Wake word detected by OWW model [%s] (score=%.2f)", model_name, score)
                            cooldown_until = now + 2.5
                            self.on_wake(model_name, None)
                            speech_buffer.clear()
                            break
                except Exception:
                    pass

            # 2. Acoustic Speech & Custom "Hey Ikkhi" Spotting
            rms = float(np.sqrt(np.mean(np.square(chunk.astype(np.float32)))))

            if rms >= silence_threshold:
                # Active speech chunk
                is_in_speech = True
                silence_chunks = 0
                speech_buffer.append(chunk)
                # Keep buffer capped to 4 seconds maximum
                if len(speech_buffer) > 50:
                    speech_buffer.pop(0)
            else:
                # Silence chunk
                if is_in_speech:
                    silence_chunks += 1
                    speech_buffer.append(chunk)

                    # After ~350ms of trailing silence (4 chunks * 80ms) and at least 0.5s of speech
                    if silence_chunks >= 4 and len(speech_buffer) >= 7:
                        is_in_speech = False
                        silence_chunks = 0
                        
                        # Process buffered speech for "Hey Ikkhi"
                        if self.stt_engine is not None:
                            full_int16 = np.concatenate(speech_buffer, axis=0)
                            float32_audio = full_int16.astype(np.float32) / 32768.0
                            speech_buffer.clear()

                            try:
                                transcript, _ = self.stt_engine.transcribe(float32_audio)
                                clean = transcript.lower().strip()
                                logger.debug("Acoustic buffer transcript: '%s'", clean)

                                # Check for phonetic variants of "Hey Ikkhi"
                                wake_keywords = [
                                    "hey ikkhi", "hey ikki", "hey eki", "hey iki",
                                    "ikkhi", "ikki", "ickey", "iki", "hi ikkhi"
                                ]
                                matched_kw = None
                                for kw in wake_keywords:
                                    if kw in clean:
                                        matched_kw = kw
                                        break

                                if matched_kw:
                                    logger.info("Custom wake-word matched: '%s' in transcript: '%s'", matched_kw, clean)
                                    cooldown_until = now + 2.5
                                    # Extract remainder command if uttered in same sentence
                                    remainder = clean.split(matched_kw, 1)[-1].strip(" ,.!?")
                                    self.on_wake("hey ikkhi", remainder if remainder else None)
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
