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
        """Route checkpoint downloads through configured proxy if enabled, or clear invalid proxies."""
        if self.network_settings and self.network_settings.use_proxy_for_downloads and self.network_settings.proxy:
            proxy = self.network_settings.proxy.strip()
            if proxy:
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy
                os.environ["ALL_PROXY"] = proxy
        else:
            # Clear proxy environment variables to prevent dead proxies from blocking local requests
            for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
                os.environ.pop(key, None)

    def load_model(self) -> None:
        """Loads Whisper weights into GPU VRAM with local-cache-first resilience."""
        if self._is_loaded:
            return

        model_size = self.audio_settings.whisper_model
        device = self.audio_settings.whisper_device
        compute_type = self.audio_settings.compute_type

        from faster_whisper import WhisperModel

        # Tier 1: Try local cache first on target device (CUDA float16) — 100% offline, zero network dependency
        try:
            logger.info("Checking local cache for faster-whisper [%s] on %s (%s)...", model_size, device, compute_type)
            self.model = WhisperModel(
                model_size_or_path=model_size,
                device=device,
                compute_type=compute_type,
                cpu_threads=4,
                local_files_only=True
            )
            self._is_loaded = True
            logger.info("Whisper model [%s] loaded from local cache onto %s.", model_size, device)
            return
        except Exception as cache_exc:
            logger.debug("Local cache hit missed (%s), proceeding to network fetch...", cache_exc)

        # Tier 2: Fetch model online on target device (CUDA float16)
        try:
            logger.info("Initializing faster-whisper [%s] on %s (%s)...", model_size, device, compute_type)
            self.model = WhisperModel(
                model_size_or_path=model_size,
                device=device,
                compute_type=compute_type,
                cpu_threads=4
            )
            self._is_loaded = True
            logger.info("Whisper model [%s] successfully loaded onto %s.", model_size, device)
            return
        except Exception as exc:
            logger.warning("Failed to initialize CUDA Whisper: %s. Attempting CPU fallback...", exc)

        # Tier 3: CPU fallback with local cache
        try:
            self.model = WhisperModel(
                model_size_or_path=model_size,
                device="cpu",
                compute_type="int8",
                local_files_only=True
            )
            self._is_loaded = True
            logger.info("Whisper model loaded on CPU fallback (local cache).")
            return
        except Exception:
            pass

        # Tier 4: Clear proxy and retry on CPU with direct connection
        try:
            for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
                os.environ.pop(key, None)
            logger.info("Retrying Whisper model load with direct connection (cleared proxy)...")
            self.model = WhisperModel(model_size_or_path=model_size, device="cpu", compute_type="int8")
            self._is_loaded = True
            logger.info("Whisper model loaded on CPU with direct connection.")
            return
        except Exception as final_exc:
            raise SpeechRecognitionError(
                f"Fatal: Could not initialize Whisper model [{model_size}] on {device} or CPU fallback: {final_exc}"
            ) from final_exc

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
            # Ensure 1D contiguous float32 array
            if audio_array.ndim > 1:
                audio_array = audio_array.flatten()
            audio_array = np.ascontiguousarray(audio_array, dtype=np.float32)

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
            confidence = float(getattr(info, "language_probability", 1.0))
            return full_text, confidence
        except Exception as exc:
            raise SpeechRecognitionError(f"Inference failure during transcription: {exc}") from exc
