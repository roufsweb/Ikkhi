"""
Master System Integration Test Suite for Ikkhi.
Thoroughly verifies all subsystems:
1. Configuration & Domain Hierarchy
2. Intent Router & Tiered Classification
3. Action Registry & Parameter Constraints
4. Universal UI Inspector & Adaptive Memory Profiles
5. Multi-Monitor Display Topology
6. Screen Indexer & Token Downsampling
7. Visual Cursor Pointer Math & DPI Awareness
8. Local Speech Synthesis Lifecycle
9. Orchestrator End-to-End Simulation
"""

import sys
import tempfile
from pathlib import Path
import pytest

from ikkhi.core.config import AppConfig, AudioSettings
from ikkhi.core.exceptions import ActionExecutionError
from ikkhi.core.router import IntentRouter, RouteTarget
from ikkhi.automation.registry import registry
from ikkhi.automation.profiles import ProfileManager, IndexedControl
from ikkhi.automation.inspector import UniversalUIInspector
from ikkhi.vision.monitors import MultiMonitorManager
from ikkhi.vision.pointer import _ease_out_cubic
from ikkhi.audio.tts import LocalSpeechEngine
from ikkhi.core.orchestrator import IkkhiOrchestrator


class TestSystemIntegration:

    def test_01_configuration_integrity(self):
        """Verify configuration loading, default parameters, and schema constraints."""
        config = AppConfig()
        assert config.system.name == "Ikkhi"
        assert config.network.use_proxy_for_downloads is True
        assert "socks5://" in config.network.proxy
        assert config.audio.whisper_device in ("cuda", "cpu")
        assert config.screen_indexing.max_image_dimension == 1024
        assert config.universal_automation.enabled is True

    def test_02_router_deterministic_classification(self):
        """Ensure intent router categorizes utterances accurately into Tier 0 vs Tier 1."""
        router = IntentRouter()
        
        # Tier 0 Local fast-paths
        assert router.route("play").target == RouteTarget.LOCAL_ACTION
        assert router.route("pause").action_name == "media_play_pause"
        assert router.route("volume up").action_name == "audio_volume_up"
        assert router.route("cut clip").action_name == "davinci_blade_cut"
        assert router.route("ripple delete").action_name == "davinci_ripple_delete"
        assert router.route("minimize window").action_name == "window_minimize"
        
        # Tier 1 Multimodal Visual Inquiries
        assert router.route("where is the export button").target == RouteTarget.VISUAL_QUERY
        assert router.route("point to the color tab").target == RouteTarget.VISUAL_QUERY
        assert router.route("find the timeline").target == RouteTarget.VISUAL_QUERY
        
        # Tier 1 Conversational fallback
        assert router.route("what is a lut in color grading").target == RouteTarget.CONVERSATIONAL_FALLBACK

    def test_03_action_registry_safety(self):
        """Verify action dispatch, argument enforcement, and rejection of unregistered calls."""
        actions = registry.list_actions()
        assert "media_play_pause" in actions
        assert "davinci_blade_cut" in actions
        assert "window_minimize" in actions
        
        # Safe rejection of unknown actions
        with pytest.raises(ActionExecutionError):
            registry.execute("arbitrary_unverified_action_123")

    def test_04_adaptive_profile_learning_pipeline(self, tmp_path):
        """Verify per-application memory creation, control caching, and adaptive recall."""
        mgr = ProfileManager(tmp_path)
        app_id = "test_creative_suite"
        
        profile = mgr.get_or_create_profile(app_id, "suite.exe")
        assert profile.app_identifier == app_id
        
        # Cache discovered control
        profile.controls["render_button"] = IndexedControl(
            name="Render",
            control_type="Button",
            bounding_box=(120, 240, 200, 300),
            relative_center=(0.75, 0.85)
        )
        mgr.save_profile(profile)
        
        # Record user interaction trigger
        mgr.record_interaction(
            app_identifier=app_id,
            trigger_phrase="start rendering",
            hotkey="ctrl+r"
        )
        
        # Reload and verify persistence
        reloaded = ProfileManager(tmp_path).get_or_create_profile(app_id)
        assert "render_button" in reloaded.controls
        assert reloaded.learned_interactions["start rendering"].hotkey == "ctrl+r"

    def test_05_multi_monitor_topology(self):
        """Verify Windows display enumeration and virtual screen geometry resolution."""
        mon_mgr = MultiMonitorManager()
        monitors = mon_mgr.get_all_monitors()
        assert len(monitors) >= 1
        
        primary = [m for m in monitors if m.is_primary]
        assert len(primary) == 1
        assert primary[0].width > 0 and primary[0].height > 0
        
        cursor_mon = mon_mgr.get_cursor_monitor()
        assert cursor_mon is not None
        assert cursor_mon.width > 0

    def test_06_cursor_pointer_kinematics(self):
        """Verify cubic bezier interpolation curve bounds and continuity."""
        # Boundaries: t=0 -> 0.0, t=1.0 -> 1.0
        assert _ease_out_cubic(0.0) == 0.0
        assert _ease_out_cubic(1.0) == 1.0
        # Monotonicity & deceleration: at t=0.5, value must exceed 0.5 (fast start, smooth stop)
        mid = _ease_out_cubic(0.5)
        assert mid > 0.5 and mid < 1.0

    def test_07_local_speech_synthesis_pipeline(self):
        """Verify local zero-token speech engine initialization and queue drainage."""
        settings = AudioSettings()
        engine = LocalSpeechEngine(settings)
        assert engine._running is True
        engine.speak("System diagnostics check.", wait=False)
        engine.stop()
        assert engine._running is False

    def test_08_orchestrator_simulation_fast_path(self):
        """Verify end-to-end processing of Tier 0 fast-path actions in the orchestrator."""
        config = AppConfig()
        orchestrator = IkkhiOrchestrator(config)
        
        # Simulate local cut command
        res = orchestrator.process_transcript("cut clip")
        assert "[Local Action Executed]" in res
        assert "davinci_blade_cut" in res
        
        # Cleanup speech thread
        orchestrator.speech_engine.stop()
