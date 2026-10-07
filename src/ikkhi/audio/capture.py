"""
Zero-Copy Audio Buffer Ingestion Engine.
Captures low-latency 16 kHz mono microphone streams into NumPy memory structures.
"""

import queue
import logging
from typing import Optional, List
import numpy as np
import sounddevice as sd
from ikkhi.core.config import AudioSettings
from ikkhi.core.exceptions import AudioDeviceError

logger = logging.getLogger(__name__)


def resolve_optimal_input_device(configured: Optional[int | str] = None) -> Optional[int]:
    """
    Resolves the physical recording device index.
    If configured explicitly, respects user preference.
    If default device is a silent virtual cable (e.g. VB-Audio Cable),
    automatically scans for and selects a real physical microphone.
    """
    if configured is not None:
        try:
            return int(configured)
        except ValueError:
            pass

    try:
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        if default_input is None or default_input < 0 or default_input >= len(devices):
            return None

        def_name = devices[default_input]["name"].lower()
        # If the default Windows input device is NOT a virtual cable, use it
        if "cable" not in def_name and "virtual" not in def_name:
            return default_input

        # Windows default is a virtual cable; find a real physical microphone
        for idx, d in enumerate(devices):
            name = d.get("name", "").lower()
            if d.get("max_input_channels", 0) > 0 and "cable" not in name and "virtual" not in name and "mapper" not in name:
                if "microphone" in name or "headset" in name:
                    logger.info("Auto-resolved physical microphone: [%d] '%s' (avoiding silent virtual cable)", idx, d["name"])
                    return idx

        # Fallback to any real physical input device (excluding stereo mix and mapper)
        for idx, d in enumerate(devices):
            name = d.get("name", "").lower()
            if d.get("max_input_channels", 0) > 0 and "cable" not in name and "virtual" not in name and "mapper" not in name and "stereo mix" not in name:
                return idx

        return default_input
    except Exception as exc:
        logger.debug("Device resolution exception: %s", exc)
        return None


class AudioCaptureEngine:
    """Manages asynchronous microphone streams and produces Whisper-ready float32 arrays."""

    def __init__(self, settings: AudioSettings) -> None:
        self.settings = settings
        self.sample_rate = settings.sample_rate # 16000 Hz
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._is_recording = False
        self._latest_rms: float = 0.0

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """High-priority audio callback pushing raw chunks onto the queue."""
        if status:
            logger.warning("Audio input status flag: %s", status)
        if self._is_recording:
            # Flatten to 1D mono float32 array and push copy into buffer queue
            chunk = indata[:, 0].copy()
            self._latest_rms = float(np.sqrt(np.mean(np.square(chunk)))) if len(chunk) > 0 else 0.0
            self._audio_queue.put(chunk)

    def get_live_rms(self) -> float:
        """Returns the RMS amplitude of the latest recorded chunk for visualizer feeds."""
        return self._latest_rms

    def start_recording(self) -> None:
        """Initiates physical audio capture from the default microphone."""
        if self._is_recording:
            return

        # Drain any residual frames
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

        self._is_recording = True
        try:
            dev_idx = resolve_optimal_input_device(getattr(self.settings, "input_device", None))

            if self._stream is None or not self._stream.active:
                self._stream = sd.InputStream(
                    device=dev_idx,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype="float32",
                    blocksize=1024,
                    callback=self._audio_callback
                )
                self._stream.start()
        except Exception as exc:
            self._is_recording = False
            raise AudioDeviceError(f"Failed to open physical audio stream: {exc}") from exc

    def stop_recording(self) -> np.ndarray:
        """
        Halts recording and extracts accumulated chunks as a single contiguous float32 NumPy array.
        Returns: NumPy array of shape (N,) containing normalized audio in [-1.0, 1.0].
        """
        self._is_recording = False
        collected_chunks: List[np.ndarray] = []

        while not self._audio_queue.empty():
            try:
                collected_chunks.append(self._audio_queue.get_nowait())
            except queue.Empty:
                break

        if not collected_chunks:
            return np.zeros(0, dtype=np.float32)

        audio_buffer = np.concatenate(collected_chunks, axis=0)
        return audio_buffer

    def compute_rms(self, audio: np.ndarray) -> float:
        """Calculates Root-Mean-Square (RMS) amplitude for voice activity detection."""
        if len(audio) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(audio))))

    def close(self) -> None:
        """Cleanly releases physical audio hardware handles."""
        self._is_recording = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
