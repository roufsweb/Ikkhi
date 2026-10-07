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


def test_audio_capture_live_rms():
    settings = AudioSettings()
    capture = AudioCaptureEngine(settings)
    assert capture.get_live_rms() == 0.0


def test_wake_word_listener_lifecycle():
    from unittest.mock import MagicMock
    from ikkhi.audio.wakeword import WakeWordListener

    settings = AudioSettings()
    mock_wake = MagicMock()
    listener = WakeWordListener(settings=settings, on_wake=mock_wake)
    assert listener._running is False
    assert listener.target_phrase == "hey ikkhi"

    # Test programmatic / manual wake trigger
    listener.trigger_manual("hey ikkhi")
    mock_wake.assert_called_once_with("hey ikkhi", None)


def test_audio_device_auto_resolution():
    from ikkhi.audio.capture import (
        resolve_optimal_device_params,
        resolve_optimal_output_device,
        get_audio_hardware_report
    )

    in_idx, in_sr, in_ch, in_name = resolve_optimal_device_params()
    assert isinstance(in_sr, int)
    assert in_sr in (16000, 44100, 48000)
    assert in_ch in (1, 2)
    assert isinstance(in_name, str)

    out_idx, out_sr, out_ch, out_name = resolve_optimal_output_device()
    assert isinstance(out_sr, int)
    assert out_sr > 0
    assert out_ch in (1, 2)
    assert isinstance(out_name, str)

    rep = get_audio_hardware_report()
    assert "host_apis" in rep
    assert "default_devices" in rep
    assert "resolved_input" in rep
    assert "resolved_output" in rep
    assert rep["resolved_input"]["sample_rate"] == in_sr
    assert rep["resolved_output"]["sample_rate"] == out_sr
