"""
Unit test suite validating defensive security hardening, path traversal protection,
and command injection immunity in Ikkhi.
"""

import pytest
from pathlib import Path
from ikkhi.automation.profiles import ProfileManager
from ikkhi.automation.registry import registry
from ikkhi.core.exceptions import ActionExecutionError
from ikkhi.core.config import AudioSettings
from ikkhi.audio.tts import LocalSpeechEngine


def test_path_traversal_mitigation(tmp_path):
    """Verify that malicious identifiers cannot traverse out of the storage directory."""
    mgr = ProfileManager(tmp_path)
    
    # Path traversal attack vectors
    adversarial_ids = [
        "../../system32/calc",
        "..\\..\\windows\\cmd",
        "/etc/passwd",
        "nested/../../escape"
    ]
    
    for bad_id in adversarial_ids:
        # Must sanitize and ensure the file is strictly contained within tmp_path
        profile = mgr.get_or_create_profile(bad_id)
        target_file = tmp_path / f"{profile.app_identifier}.json"
        assert target_file.exists(), f"Target file should be safely contained in {tmp_path}"
        assert target_file.resolve().is_relative_to(tmp_path.resolve())


def test_tts_injection_immunity():
    """Verify that adversarial characters and shell sequences are safely handled without executing."""
    settings = AudioSettings()
    engine = LocalSpeechEngine(settings)
    
    # Adversarial payloads attempting shell breakout
    payloads = [
        'Test"; Write-Host "Injected"; #',
        "$(whoami)",
        "`calc`",
        "Test & calc.exe &"
    ]
    
    for payload in payloads:
        # Must not raise an unhandled exception or break out of process
        engine.speak(payload)
    
    engine.stop()


def test_registry_arbitrary_execution_guard():
    """Verify that unregistered, arbitrary function calls are strictly rejected."""
    with pytest.raises(ActionExecutionError):
        registry.execute("os.system", {"command": "dir"})
        
    with pytest.raises(ActionExecutionError):
        registry.execute("__import__('os').system", {})
