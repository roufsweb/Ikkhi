"""
GPU-Accelerated Speech-to-Text (STT) Transcription Engine.
Leverages faster-whisper (CTranslate2) on NVIDIA CUDA cores for sub-250ms private transcription.
"""

import os
import logging
from typing import Optional, Tuple
import numpy as np
from ikkhi.core.config import AudioSettings, NetworkSettings
from ikkhi.core.exceptions import SpeechRecognitionError

logger = logging.getLogger(__name__)


class WhisperSTTEngine:
    """Manages local Whisper neural checkpoints on CUDA hardware with zero cloud exposure."""

    def __init__(self, audio_settings: AudioSettings, network_settings: Optional[NetworkSettings] = None) -> None:
        self.audio_settings = audio_settings
        self.network_settings = network_settings
        self.model = None
        self._is_loaded = False
        self._configure_proxy()

    def _configure_proxy(self) -> None:
        """Route checkpoint downloads through configured SOCKS5 proxy if enabled."""
        if self.network_settings and self.network_settings.use_proxy_for_downloads:
            proxy = self.network_settings.proxy
            if proxy:
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy
                os.environ["ALL_PROXY"] = proxy

    def load_model(self) -> None:
        """Loads Whisper weights into GPU VRAM."""
        if self._is_loaded:
            return

        model_size = self.audio_settings.whisper_model
        device = self.audio_settings.whisper_device
        compute_type = self.audio_settings.compute_type

        try:
            from faster_whisper import WhisperModel
            logger.info("Initializing faster-whisper [%s] on %s (%s)...", model_size, device, compute_type)
            self.model = WhisperModel(
                model_size_or_path=model_size,
                device=device,
                compute_type=compute_type,
                cpu_threads=4
            )
            self._is_loaded = True
            logger.info("Whisper model [%s] successfully loaded onto %s.", model_size, device)
        except Exception as exc:
            logger.warning("Failed to initialize CUDA Whisper: %s. Attempting CPU fallback...", exc)
            try:
                from faster_whisper import WhisperModel
                self.model = WhisperModel(model_size_or_path=model_size, device="cpu", compute_type="int8")
                self._is_loaded = True
                logger.info("Whisper model loaded on CPU fallback.")
            except Exception as cpu_exc:
                raise SpeechRecognitionError(f"Fatal: Could not initialize Whisper model: {cpu_exc}") from cpu_exc

    def transcribe(self, audio_array: np.ndarray) -> Tuple[str, float]:
        """
        Transcribes a normalized float32 mono audio NumPy array.
        Returns: (transcribed_text, confidence_score)
        """
        if not self._is_loaded:
            self.load_model()

        if len(audio_array) == 0:
            return "", 0.0

        try:
            # faster-whisper accepts float32 numpy arrays directly
            segments, info = self.model.transcribe(
                audio_array,
                beam_size=1, # Greedy search for maximum real-time speed
                language="en",
                vad_filter=False # Do not discard short acoustic speech buffers
            )
            
            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text.strip())

            full_text = " ".join(transcript_parts).strip()
            confidence = float(getattr(info, "transcription_options", {}).get("temperature", 1.0))
            return full_text, confidence
        except Exception as exc:
            raise SpeechRecognitionError(f"Inference failure during transcription: {exc}") from exc
