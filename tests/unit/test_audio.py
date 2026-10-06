"""
Unit tests for the AudioCaptureEngine and PushToTalkListener subsystems.
"""

import numpy as np
from ikkhi.core.config import AudioSettings
from ikkhi.audio.capture import AudioCaptureEngine
from ikkhi.audio.hotkey import PushToTalkListener


def test_audio_capture_rms_computation():
    settings = AudioSettings()
    capture = AudioCaptureEngine(settings)
    
    # Silence has 0 RMS
    silence = np.zeros(16000, dtype=np.float32)
    assert capture.compute_rms(silence) == 0.0
    
    # Sine wave has expected RMS = peak / sqrt(2)
    t = np.linspace(0, 1, 16000, endpoint=False)
    sine = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    rms = capture.compute_rms(sine)
    assert 0.69 < rms < 0.72


def test_hotkey_listener_initialization():
    settings = AudioSettings()
    listener = PushToTalkListener(settings)
    assert listener._is_active is False
    assert listener.settings.push_to_talk_key == "ctrl+alt+space"
