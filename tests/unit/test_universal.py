"""
Unit tests for the Universal App Inspector, Adaptive Profiles, and Dynamic Learning.
"""

from ikkhi.automation.profiles import ProfileManager, AppProfile, IndexedControl


def test_profile_creation_and_persistence(tmp_path):
    mgr = ProfileManager(tmp_path)
    profile = mgr.get_or_create_profile("davinci_resolve", "resolve.exe")
    assert profile.app_identifier == "davinci_resolve"
    assert "resolve.exe" in profile.process_names

    # Add a control
    profile.controls["export"] = IndexedControl(
        name="Export",
        control_type="Button",
        bounding_box=(100, 200, 150, 250),
        relative_center=(0.85, 0.90)
    )
    mgr.save_profile(profile)

    # Re-instantiate manager and check that it persisted
    mgr2 = ProfileManager(tmp_path)
    profile2 = mgr2.get_or_create_profile("davinci_resolve")
    assert "export" in profile2.controls
    assert profile2.controls["export"].name == "Export"


def test_learned_interaction_recording(tmp_path):
    mgr = ProfileManager(tmp_path)
    mgr.record_interaction(
        app_identifier="chrome",
        trigger_phrase="open new tab",
        hotkey="ctrl+t"
    )

    profile = mgr.get_or_create_profile("chrome")
    assert "open new tab" in profile.learned_interactions
    interaction = profile.learned_interactions["open new tab"]
    assert interaction.hotkey == "ctrl+t"
    assert interaction.success_count == 1

    # Record second time to verify frequency increment
    mgr.record_interaction(
        app_identifier="chrome",
        trigger_phrase="open new tab",
        hotkey="ctrl+t"
    )
    profile = mgr.get_or_create_profile("chrome")
    assert profile.learned_interactions["open new tab"].success_count == 2
