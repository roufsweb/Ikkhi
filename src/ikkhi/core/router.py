"""
Intent routing subsystem: Dispatches user transcripts to either the Tier 0 Local Fast-Path
or the Tier 1 Multimodal AI Fallback.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class RouteTarget(str, Enum):
    LOCAL_ACTION = "local_action"
    VISUAL_QUERY = "visual_query"
    CONVERSATIONAL_FALLBACK = "conversational_fallback"
    UNMATCHED = "unmatched"


@dataclass(frozen=True)
class IntentRoute:
    target: RouteTarget
    action_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    raw_query: str = ""
    is_cloud_request: bool = False


class IntentRouter:
    """High-throughput, deterministic router designed to bypass cloud latency and token costs."""

    # Fast-path pattern definitions: (Compiled regex, Action identifier, default kwargs)
    LOCAL_PATTERNS = [
        # Media & Playback controls
        (re.compile(r"^\b(play|pause|resume|toggle playback)\b", re.IGNORECASE), "media_play_pause", {}),
        (re.compile(r"^\b(stop|halt playback)\b", re.IGNORECASE), "media_stop", {}),
        (re.compile(r"^\b(mute|unmute|toggle audio mute)\b", re.IGNORECASE), "audio_toggle_mute", {}),
        (re.compile(r"^\bvolume\s+up\b", re.IGNORECASE), "audio_volume_up", {"step": 5}),
        (re.compile(r"^\bvolume\s+down\b", re.IGNORECASE), "audio_volume_down", {"step": 5}),

        # Video Editing Actions (e.g. DaVinci Resolve)
        (re.compile(r"^\b(cut|blade|split clip|make cut)\b", re.IGNORECASE), "davinci_blade_cut", {}),
        (re.compile(r"^\b(ripple delete|delete gap)\b", re.IGNORECASE), "davinci_ripple_delete", {}),
        (re.compile(r"^\b(add marker|mark frame)\b", re.IGNORECASE), "davinci_add_marker", {}),
        (re.compile(r"^\b(save project|quick save)\b", re.IGNORECASE), "app_save", {}),

        # Window & OS controls
        (re.compile(r"^\b(minimize window|minimize this)\b", re.IGNORECASE), "window_minimize", {}),
        (re.compile(r"^\b(maximize window|fullscreen)\b", re.IGNORECASE), "window_maximize", {}),
        (re.compile(r"^\b(open terminal|new terminal)\b", re.IGNORECASE), "os_open_terminal", {}),
    ]

    # Visual pointer / screen query indicators
    VISUAL_INDICATORS = re.compile(
        r"\b(where is|point to|point out|show me|find the|locate|what is this|explain screen)\b",
        re.IGNORECASE
    )

    def route(self, transcript: str) -> IntentRoute:
        clean_text = transcript.strip()
        if not clean_text:
            return IntentRoute(target=RouteTarget.UNMATCHED, raw_query="")

        # 1. Tier 0: Direct deterministic local match (0 credits, <1ms)
        for pattern, action_name, params in self.LOCAL_PATTERNS:
            if pattern.search(clean_text):
                return IntentRoute(
                    target=RouteTarget.LOCAL_ACTION,
                    action_name=action_name,
                    parameters=params,
                    raw_query=clean_text,
                    is_cloud_request=False
                )

        # 2. Check for explicit Visual Screen / Pointing queries
        if self.VISUAL_INDICATORS.search(clean_text):
            return IntentRoute(
                target=RouteTarget.VISUAL_QUERY,
                raw_query=clean_text,
                is_cloud_request=True
            )

        # 3. Tier 1: Fallback to conversational AI
        return IntentRoute(
            target=RouteTarget.CONVERSATIONAL_FALLBACK,
            raw_query=clean_text,
            is_cloud_request=True
        )
