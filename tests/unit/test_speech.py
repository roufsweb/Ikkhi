"""
Unit tests for the LocalSpeechEngine subsystem.
"""

from ikkhi.core.config import AudioSettings
from ikkhi.audio.tts import LocalSpeechEngine


def test_speech_engine_lifecycle():
    settings = AudioSettings()
    engine = LocalSpeechEngine(settings)
    assert engine._running is True
    # Test enqueue without crash
    engine.speak("Testing Ikkhi local speech.")
    engine.stop()
    assert engine._running is False
