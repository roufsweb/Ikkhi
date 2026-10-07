"""
Natural Neural Text-to-Speech (TTS) Synthesis Subsystem.
Provides Google Assistant-quality neural voices via Edge Neural TTS with zero API cost,
and falls back gracefully to offline Windows SAPI when offline.
"""

import io
import sys
import queue
import logging
import asyncio
import threading
from typing import Optional
import numpy as np

from ikkhi.core.config import AudioSettings

logger = logging.getLogger("ikkhi.audio.tts")


class LocalSpeechEngine:
    """
    Dual-engine speech synthesizer:
    - Primary: Microsoft Edge Neural TTS (sounds like Google Assistant, buttery smooth and conversational)
    - Fallback: Native Windows SAPI 5 (100% offline fallback)
    """

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
        """Enqueues text for spoken synthesis."""
        clean_text = text.strip()
        if not clean_text:
            return

        if wait:
            self._synthesize(clean_text)
        else:
            self._queue.put(clean_text)

    def _speech_worker(self) -> None:
        """Worker loop processing spoken text from the queue."""
        # Initialize COM on this worker thread if SAPI fallback is used
        try:
            import ctypes
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
        """Synthesizes text using Neural TTS first, with SAPI fallback."""
        clean_text = text.strip()
        if not clean_text:
            return

        # Attempt Neural voice if configured
        if getattr(self.settings, "tts_engine", "neural") == "neural":
            if self._synthesize_neural(clean_text):
                return
            logger.info("Neural TTS failed or offline; falling back to offline SAPI voice.")

        # Fallback to local SAPI voice
        self._synthesize_sapi(clean_text)

    def _synthesize_neural(self, text: str) -> bool:
        """Synthesize natural neural voice using edge-tts streamed directly to sounddevice."""
        try:
            import edge_tts
            import av
            import sounddevice as sd

            voice = getattr(self.settings, "tts_voice", "en-US-AvaNeural")
            rate = getattr(self.settings, "tts_rate", "+0%")
            pitch = getattr(self.settings, "tts_pitch", "+0Hz")

            async def _generate_audio_bytes() -> bytes:
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
                chunks: list[bytes] = []
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        chunks.append(chunk["data"])
                return b"".join(chunks)

            # Run async generator in dedicated event loop
            audio_bytes = asyncio.run(_generate_audio_bytes())
            if not audio_bytes:
                return False

            # Decode MP3 bytes in-memory using PyAV to PCM float32
            container = av.open(io.BytesIO(audio_bytes))
            stream = container.streams.audio[0]
            target_sample_rate = 24000
            resampler = av.AudioResampler(format="fltp", layout="mono", rate=target_sample_rate)

            frames = []
            for frame in container.decode(stream):
                for resampled in resampler.resample(frame):
                    frames.append(resampled.to_ndarray().squeeze())
            container.close()

            if not frames:
                return False

            pcm_data = np.concatenate(frames)
            # Output device resolution
            device_id = getattr(self.settings, "output_device", None)
            sd.play(pcm_data, samplerate=target_sample_rate, device=device_id)
            sd.wait()
            return True
        except Exception as exc:
            logger.debug("Neural TTS synthesis error: %s", exc)
            return False

    def _synthesize_sapi(self, text: str) -> None:
        """Synthesizes text locally using native Windows SAPI without shell execution."""
        # Tier A: Direct in-process Win32 SAPI via COM
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
            return
        except Exception:
            pass

        # Tier B: Direct comtypes SAPI call
        try:
            import comtypes.client
            speaker = comtypes.client.CreateObject("SAPI.SpVoice")
            speaker.Speak(text)
            return
        except Exception:
            pass

        # Tier C: Parameterized PowerShell fallback via standard input
        try:
            import subprocess
            script = [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "$input_text = [Console]::In.ReadToEnd(); Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak($input_text)"
            ]
            subprocess.run(script, input=text, text=True, capture_output=True, timeout=10)
        except Exception as exc:
            logger.error("Failed to synthesize speech via SAPI fallback: %s", exc)

    def stop(self) -> None:
        """Gracefully terminate speech synthesis thread."""
        self._running = False
        try:
            import sounddevice as sd
            sd.stop()
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
