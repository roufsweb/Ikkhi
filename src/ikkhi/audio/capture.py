"""
Zero-Copy Audio Buffer Ingestion Engine.
Captures low-latency 16 kHz mono microphone streams into NumPy memory structures.
"""

import time
import queue
import logging
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import sounddevice as sd
from ikkhi.core.config import AudioSettings
from ikkhi.core.exceptions import AudioDeviceError

logger = logging.getLogger(__name__)


def probe_device_stream_params(dev_idx: int) -> Optional[Tuple[int, int]]:
    """
    Tests opening a non-blocking stream on dev_idx across common sample rates and channels.
    Uses PortAudio hardware check and immediate stream initialization.
    Returns (sample_rate, channels) on first successful configuration, or None if device cannot stream.
    """
    candidates = [
        (16000, 1),
        (44100, 1),
        (44100, 2),
        (48000, 1),
        (48000, 2),
    ]
    for sr, ch in candidates:
        try:
            sd.check_input_settings(device=dev_idx, samplerate=sr, channels=ch)
            stream = sd.InputStream(
                device=dev_idx,
                samplerate=sr,
                channels=ch,
                dtype="float32",
            )
            stream.start()
            time.sleep(0.02)
            stream.stop()
            stream.close()
            return (sr, ch)
        except Exception:
            continue
    return None


def resolve_optimal_device_params(configured: Optional[int | str] = None) -> Tuple[Optional[int], int, int, str]:
    """
    Intelligently identifies and verifies a working recording device, returning:
    (device_index, native_sample_rate, channels, device_name).
    Prioritizes real physical USB microphones and active Windows defaults over virtual cables and unplugged jacks.
    Guarantees that the resolved device will not crash PortAudio with PaErrorCode -9996.
    """
    try:
        devices = sd.query_devices()
        apis = [a["name"] for a in sd.query_hostapis()]
    except Exception as exc:
        logger.debug("Failed to query devices: %s", exc)
        return (None, 16000, 1, "Default Device")

    # 1. If explicitly configured by user, probe that specific index
    if configured is not None:
        try:
            cfg_idx = int(configured)
            if 0 <= cfg_idx < len(devices):
                params = probe_device_stream_params(cfg_idx)
                if params is not None:
                    dname = devices[cfg_idx].get("name", f"Device [{cfg_idx}]")
                    logger.info("Using configured audio device: [%d] '%s' (%dHz, %dch)", cfg_idx, dname, params[0], params[1])
                    return (cfg_idx, params[0], params[1], dname)
                else:
                    logger.warning("Configured device [%d] failed PortAudio streaming probe. Falling back to auto-detection.", cfg_idx)
        except (ValueError, TypeError):
            pass

    # 2. Check Windows System Default Input device first
    try:
        def_idx = sd.default.device[0]
        if def_idx is not None and 0 <= def_idx < len(devices):
            d = devices[def_idx]
            dname = d.get("name", "").lower()
            # If default input is a legitimate physical mic (not virtual cable, stereo mix, or loopback), probe it
            if "cable" not in dname and "virtual" not in dname and "stereo mix" not in dname and "line in" not in dname:
                params = probe_device_stream_params(def_idx)
                if params is not None:
                    api = apis[d.get("hostapi", 0)] if d.get("hostapi", 0) < len(apis) else ""
                    logger.info("Auto-resolved active default microphone: [%d] (%s) '%s' (%dHz, %dch)", def_idx, api, d["name"], params[0], params[1])
                    return (def_idx, params[0], params[1], d["name"])
    except Exception as exc:
        logger.debug("Default input probe error: %s", exc)

    # 3. Scan all devices for physical microphones (USB first, then Headset, then other mics), prioritizing MME / WASAPI
    candidate_devices = []
    for idx, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            name = d.get("name", "").lower()
            hostapi = d.get("hostapi", 0)
            if "cable" not in name and "virtual" not in name and "stereo mix" not in name and "line in" not in name:
                is_usb = "usb" in name
                is_physical = any(k in name for k in ("mic", "headset", "array", "realtek"))
                
                # Priority tiering:
                # 0: Physical USB microphone on MME (0) or WASAPI (2)
                # 1: Physical USB microphone on DirectSound (1)
                # 2: Other physical headset/mic on MME/WASAPI
                # 3: Other physical headset/mic on DirectSound
                # 50+: WDM-KS (avoid exclusive kernel streaming lock unless absolutely nothing else exists)
                if hostapi == 3:  # WDM-KS
                    priority = 50 if is_usb else 60
                elif is_usb:
                    priority = 0 if hostapi in (0, 2) else 1
                elif is_physical and "realtek" not in name:
                    priority = 2 if hostapi in (0, 2) else 3
                elif is_physical:
                    priority = 4 if hostapi in (0, 2) else 5
                else:
                    priority = 10

                candidate_devices.append((priority, idx, d))

    candidate_devices.sort(key=lambda x: x[0])

    for _, idx, d in candidate_devices:
        params = probe_device_stream_params(idx)
        if params is not None:
            api = apis[d.get("hostapi", 0)] if d.get("hostapi", 0) < len(apis) else ""
            logger.info("Auto-resolved active physical microphone: [%d] (%s) '%s' (%dHz, %dch)", idx, api, d["name"], params[0], params[1])
            return (idx, params[0], params[1], d["name"])

    # 4. Fallback to device 0 (Microsoft Sound Mapper)
    if len(devices) > 0:
        params = probe_device_stream_params(0)
        if params is not None:
            return (0, params[0], params[1], devices[0].get("name", "Device [0]"))

    return (None, 16000, 1, "Default Audio Device")


def resolve_optimal_output_device(configured: Optional[int | str] = None) -> Tuple[Optional[int], int, int, str]:
    """
    Intelligently identifies and verifies a working playback device (speakers / headphones), returning:
    (device_index, native_sample_rate, channels, device_name).
    Prioritizes real headphones/speakers over virtual cable loopbacks.
    """
    try:
        devices = sd.query_devices()
        apis = [a["name"] for a in sd.query_hostapis()]
    except Exception as exc:
        logger.debug("Failed to query output devices: %s", exc)
        return (None, 44100, 2, "Default Output Device")

    # 1. User configured output device
    if configured is not None:
        try:
            cfg_idx = int(configured)
            if 0 <= cfg_idx < len(devices) and devices[cfg_idx].get("max_output_channels", 0) > 0:
                d = devices[cfg_idx]
                sr = int(d.get("default_samplerate", 44100))
                ch = min(2, d.get("max_output_channels", 2))
                try:
                    sd.check_output_settings(device=cfg_idx, samplerate=sr, channels=ch)
                    dname = d.get("name", f"Device [{cfg_idx}]")
                    logger.info("Using configured output audio device: [%d] '%s' (%dHz, %dch)", cfg_idx, dname, sr, ch)
                    return (cfg_idx, sr, ch, dname)
                except Exception:
                    pass
        except (ValueError, TypeError):
            pass

    # 2. Check Windows Default Output device
    try:
        def_idx = sd.default.device[1]
        if def_idx is not None and 0 <= def_idx < len(devices):
            d = devices[def_idx]
            dname = d.get("name", "").lower()
            if "cable" not in dname and "virtual" not in dname:
                sr = int(d.get("default_samplerate", 44100))
                ch = min(2, d.get("max_output_channels", 2))
                try:
                    sd.check_output_settings(device=def_idx, samplerate=sr, channels=ch)
                    api = apis[d.get("hostapi", 0)] if d.get("hostapi", 0) < len(apis) else ""
                    logger.info("Auto-resolved active default speaker/headphones: [%d] (%s) '%s' (%dHz, %dch)", def_idx, api, d["name"], sr, ch)
                    return (def_idx, sr, ch, d["name"])
                except Exception:
                    pass
    except Exception as exc:
        logger.debug("Default output probe error: %s", exc)

    # 3. Scan all output devices for physical headphones/speakers
    candidate_devices = []
    for idx, d in enumerate(devices):
        if d.get("max_output_channels", 0) > 0:
            name = d.get("name", "").lower()
            hostapi = d.get("hostapi", 0)
            if "cable" not in name and "virtual" not in name:
                is_physical = any(k in name for k in ("headphone", "speaker", "audio", "x-528", "realtek"))
                priority = 0 if is_physical and hostapi in (0, 2) else (1 if is_physical and hostapi == 1 else (2 if is_physical else 3))
                candidate_devices.append((priority, idx, d))

    candidate_devices.sort(key=lambda x: x[0])

    for _, idx, d in candidate_devices:
        sr = int(d.get("default_samplerate", 44100))
        ch = min(2, d.get("max_output_channels", 2))
        try:
            sd.check_output_settings(device=idx, samplerate=sr, channels=ch)
            api = apis[d.get("hostapi", 0)] if d.get("hostapi", 0) < len(apis) else ""
            logger.info("Auto-resolved active physical output: [%d] (%s) '%s' (%dHz, %dch)", idx, api, d["name"], sr, ch)
            return (idx, sr, ch, d["name"])
        except Exception:
            continue

    return (None, 44100, 2, "Default Output Device")


def get_audio_hardware_report() -> Dict[str, Any]:
    """
    Comprehensive diagnostic report enumerating host audio APIs, connected endpoints,
    Windows CoreAudio jack states, and resolved routing paths.
    """
    devices = sd.query_devices()
    apis = [a["name"] for a in sd.query_hostapis()]

    # CoreAudio physical status
    core_audio = []
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Capture")
        for i in range(winreg.QueryInfoKey(k)[0]):
            sub = winreg.EnumKey(k, i)
            sk = winreg.OpenKey(k, sub)
            state, _ = winreg.QueryValueEx(sk, "DeviceState")
            try:
                pk = winreg.OpenKey(sk, "Properties")
                name, _ = winreg.QueryValueEx(pk, "{a45c254e-df1c-4efd-8020-67d146a850e0},2")
                desc, _ = winreg.QueryValueEx(pk, "{b3f8fa53-0004-438e-9003-51a46e139bfc},6")
                status_str = "ACTIVE (Connected)" if state == 1 else ("UNPLUGGED" if state == 8 else "DISABLED")
                core_audio.append({"name": name, "desc": desc, "state": state, "status": status_str})
            except Exception:
                pass
    except Exception:
        pass

    in_idx, in_sr, in_ch, in_name = resolve_optimal_device_params()
    out_idx, out_sr, out_ch, out_name = resolve_optimal_output_device()

    return {
        "host_apis": apis,
        "default_devices": list(sd.default.device),
        "core_audio_endpoints": core_audio,
        "resolved_input": {
            "device_index": in_idx,
            "device_name": in_name,
            "sample_rate": in_sr,
            "channels": in_ch,
        },
        "resolved_output": {
            "device_index": out_idx,
            "device_name": out_name,
            "sample_rate": out_sr,
            "channels": out_ch,
        }
    }


def resolve_optimal_input_device(configured: Optional[int | str] = None) -> Optional[int]:
    """Backward-compatible helper returning solely the verified device index."""
    idx, _, _, _ = resolve_optimal_device_params(configured)
    return idx


class AudioCaptureEngine:
    """Manages asynchronous microphone streams and produces Whisper-ready float32 arrays."""

    def __init__(self, settings: AudioSettings) -> None:
        self.settings = settings
        self.target_sample_rate = settings.sample_rate  # 16000 Hz
        self.sample_rate = settings.sample_rate  # backward compatibility
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._is_recording = False
        self._latest_rms: float = 0.0
        self._native_sample_rate = 16000
        self._native_channels = 1
        self._resolved_device: Optional[int] = None
        self._device_name: str = "Default"

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """High-priority audio callback pushing raw chunks onto the queue."""
        if status:
            logger.warning("Audio input status flag: %s", status)
        if self._is_recording:
            # Multi-channel to mono downmix
            if indata.ndim > 1 and indata.shape[1] > 1:
                chunk = np.mean(indata, axis=1, dtype=np.float32)
            else:
                chunk = indata[:, 0].copy() if indata.ndim > 1 else indata.flatten().copy()
            self._latest_rms = float(np.sqrt(np.mean(np.square(chunk)))) if len(chunk) > 0 else 0.0
            self._audio_queue.put(chunk)

    def get_live_rms(self) -> float:
        """Returns the RMS amplitude of the latest recorded chunk for visualizer feeds."""
        return self._latest_rms

    def start_recording(self) -> None:
        """Initiates physical audio capture with adaptive hardware negotiation."""
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
            dev_idx, native_sr, native_ch, dev_name = resolve_optimal_device_params(
                getattr(self.settings, "input_device", None)
            )
            self._resolved_device = dev_idx
            self._native_sample_rate = native_sr
            self._native_channels = native_ch
            self._device_name = dev_name

            if self._stream is None or not self._stream.active:
                block_size = max(512, int(native_sr * 0.08))  # ~80ms blocks
                self._stream = sd.InputStream(
                    device=dev_idx,
                    samplerate=native_sr,
                    channels=native_ch,
                    dtype="float32",
                    blocksize=block_size,
                    callback=self._audio_callback
                )
                self._stream.start()
        except Exception as exc:
            self._is_recording = False
            raise AudioDeviceError(f"Failed to open physical audio stream: {exc}") from exc

    def stop_recording(self) -> np.ndarray:
        """
        Halts recording and extracts accumulated chunks as a single contiguous float32 NumPy array.
        Automatically resamples native hardware rates (e.g. 44.1kHz / 48kHz) to 16kHz for Whisper.
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

        # Resample to 16,000 Hz if hardware was captured at native rate
        if self._native_sample_rate != self.target_sample_rate and len(audio_buffer) > 0:
            target_length = int(len(audio_buffer) * self.target_sample_rate / self._native_sample_rate)
            if target_length > 0:
                try:
                    import scipy.signal
                    audio_buffer = scipy.signal.resample(audio_buffer, target_length).astype(np.float32)
                except Exception as exc:
                    logger.debug("Resampling fallback: %s", exc)

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
