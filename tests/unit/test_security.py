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


def test_screen_indexer_security_shield():
    """Verify that sensitive processes and credential managers are strictly blocked from capture."""
    from ikkhi.core.config import ScreenIndexingSettings
    from ikkhi.core.exceptions import ScreenSecurityViolation
    from ikkhi.vision.indexer import ScreenIndexer

    settings = ScreenIndexingSettings(security_shield_enabled=True)
    indexer = ScreenIndexer(settings)

    # 1. Blocked process names
    with pytest.raises(ScreenSecurityViolation):
        indexer._check_security_shield("Bitwarden.exe", "Vault - Bitwarden")

    with pytest.raises(ScreenSecurityViolation):
        indexer._check_security_shield("1Password.exe", "1Password")

    with pytest.raises(ScreenSecurityViolation):
        indexer._check_security_shield("KeePassXC.exe", "Passwords.kdbx")

    # 2. Blocked sensitive window titles
    with pytest.raises(ScreenSecurityViolation):
        indexer._check_security_shield("chrome.exe", "Enter Master Password")

    with pytest.raises(ScreenSecurityViolation):
        indexer._check_security_shield("firefox.exe", "Bank Login - Account Access")

    # 3. Permitted normal applications
    indexer._check_security_shield("code.exe", "Ikkhi - Visual Studio Code")
    indexer._check_security_shield("blender.exe", "Blender Render Canvas")


def test_indexed_screen_live_coordinates():
    """Verify IndexedScreen coordinates and movement fallback."""
    from ikkhi.vision.indexer import IndexedScreen

    screen = IndexedScreen(
        image_bytes=b"dummy",
        mime_type="image/webp",
        original_window_box=(100, 200, 500, 600),  # w=400, h=400
        scaled_dimensions=(400, 400),
        scale_factor_x=1.0,
        scale_factor_y=1.0,
        payload_kb=12.5,
        estimated_tokens=258,
        window_hwnd=0  # No live hwnd, uses fallback
    )

    x, y = screen.map_to_screen_coordinates(0.5, 0.5)
    assert x == 300
    assert y == 400
    assert screen.payload_kb == 12.5
    assert screen.estimated_tokens == 258

