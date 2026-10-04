"""
Central Application Orchestrator for Ikkhi.
Coordinates audio triggers, intent routing, hybrid execution, and visual cursor pointing.
"""

import logging
from typing import Optional
from ikkhi.core.config import AppConfig
from ikkhi.core.router import IntentRouter, RouteTarget, IntentRoute
from ikkhi.automation.registry import registry
import ikkhi.automation.windows  # registers Windows actions
import ikkhi.automation.apps.davinci  # registers DaVinci actions
from ikkhi.vision.indexer import ScreenIndexer
from ikkhi.vision.pointer import CursorPointer
from ikkhi.ai.gemini import GeminiVisualClient

logger = logging.getLogger(__name__)


class IkkhiOrchestrator:
    """Core runtime engine driving user intent resolution and deterministic execution."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.router = IntentRouter()
        self.screen_indexer = ScreenIndexer(config.screen_indexing)
        self.cursor_pointer = CursorPointer(config.pointer)
        self.gemini_client = GeminiVisualClient(config.ai_tier)

    def process_transcript(self, transcript: str) -> str:
        """Processes a transcribed user utterance through the dual-tier routing architecture."""
        route: IntentRoute = self.router.route(transcript)

        # Tier 0: Local Fast-Path (0 Tokens, <1ms)
        if route.target == RouteTarget.LOCAL_ACTION and route.action_name:
            logger.info("Executing local fast-path action: %s", route.action_name)
            try:
                registry.execute(route.action_name, route.parameters)
                return f"[Local Action Executed] {route.action_name}"
            except Exception as exc:
                logger.error("Local action failed: %s", exc)
                return f"[Error] Action {route.action_name} failed: {exc}"

        # Tier 1: Visual Screen Grounding & Pointing
        if route.target == RouteTarget.VISUAL_QUERY:
            logger.info("Routing visual query to Gemini with active window snapshot...")
            try:
                screen = self.screen_indexer.capture_active_window()
                res = self.gemini_client.query_visual_target(route.raw_query, screen)
                
                if res.target_found and res.coordinates:
                    norm_x, norm_y = res.coordinates
                    abs_x, abs_y = screen.map_to_screen_coordinates(norm_x, norm_y)
                    logger.info("Pointing cursor to physical coordinates: (%d, %d)", abs_x, abs_y)
                    self.cursor_pointer.point_to(abs_x, abs_y)
                
                return res.response_text
            except Exception as exc:
                logger.error("Visual processing failed: %s", exc)
                return f"[Error] Screen indexing failed: {exc}"

        # Tier 1: General Conversational Fallback
        if route.target == RouteTarget.CONVERSATIONAL_FALLBACK:
            return "Command not recognized locally. Conversational query handled."

        return "No action taken."
