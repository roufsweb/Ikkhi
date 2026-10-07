import logging
from typing import Optional
from ikkhi.core.config import AppConfig
from ikkhi.core.router import IntentRouter, RouteTarget, IntentRoute
from ikkhi.core.exceptions import ScreenSecurityViolation
from ikkhi.automation.registry import registry

import ikkhi.automation.windows  # registers Windows actions
import ikkhi.automation.apps.davinci  # registers DaVinci actions
from ikkhi.automation.reader import get_screen_reader  # registers screen reading action
from ikkhi.automation.universal import UniversalAutomationEngine
from ikkhi.vision.indexer import ScreenIndexer
from ikkhi.vision.pointer import CursorPointer
from ikkhi.ai.gemini import GeminiVisualClient
from ikkhi.audio.tts import LocalSpeechEngine

logger = logging.getLogger(__name__)


class IkkhiOrchestrator:
    """Core runtime engine driving user intent resolution, dynamic indexing, and adaptive execution."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.router = IntentRouter()
        self.screen_indexer = ScreenIndexer(config.screen_indexing)
        self.cursor_pointer = CursorPointer(config.pointer)
        self.gemini_client = GeminiVisualClient(config.ai_tier)
        self.universal_engine = UniversalAutomationEngine(config.universal_automation, self.cursor_pointer)
        self.speech_engine = LocalSpeechEngine(config.audio)
        self.screen_reader = get_screen_reader(self.speech_engine)

    def process_transcript(self, transcript: str) -> str:
        """Processes a transcribed user utterance through the dual-tier routing architecture."""
        route: IntentRoute = self.router.route(transcript)

        # Tier 0: Direct deterministic local action (Fastest, 0 Tokens)
        if route.target == RouteTarget.LOCAL_ACTION and route.action_name:
            logger.info("Executing local fast-path action: %s", route.action_name)
            try:
                registry.execute(route.action_name, route.parameters)
                return f"[Local Action Executed] {route.action_name}"
            except Exception as exc:
                logger.error("Local action failed: %s", exc)
                return f"[Error] Action {route.action_name} failed: {exc}"

        # Tier 0.5: Universal Adaptive App-Level Automation
        if self.config.universal_automation.enabled:
            success, msg = self.universal_engine.execute_for_active_app(transcript)
            if success:
                return f"[Universal Action Executed] {msg}"

        # Tier 1: Visual Screen Grounding & Assistive Guidance
        if route.target == RouteTarget.VISUAL_QUERY:
            context = self.universal_engine.inspector.get_foreground_context()

            # Step A: Tier 1.0 Local UIA Fast-Path (<25ms, 0 tokens, $0.00 cost)
            if context and context.hwnd:
                local_ctrl = self.universal_engine.inspector.find_control_by_label(
                    hwnd=context.hwnd,
                    query=route.raw_query
                )
                if local_ctrl:
                    box = local_ctrl.bounding_box
                    target_x = (box[0] + box[2]) // 2
                    target_y = (box[1] + box[3]) // 2
                    logger.info(
                        "Local UIA Fast-Path matched '%s' (%s) at (%d, %d)",
                        local_ctrl.name, local_ctrl.control_type, target_x, target_y
                    )
                    self.cursor_pointer.point_to(target_x, target_y)
                    explanation = f"I located {local_ctrl.name} on your screen."
                    self.speech_engine.speak(explanation)
                    return f"[Local UIA Grounded] {local_ctrl.name}"

            # Step B: Tier 1.1 Multimodal Cloud Visual Grounding (WebP crop fallback)
            logger.info("Local UIA did not match; routing visual query to Gemini with active window snapshot...")
            try:
                screen = self.screen_indexer.capture_active_window()
                logger.info(
                    "Captured active window [%s]: %dx%d, %.1f KB (%s), ~%d tokens",
                    screen.window_title,
                    screen.scaled_dimensions[0], screen.scaled_dimensions[1],
                    screen.payload_kb, screen.mime_type, screen.estimated_tokens
                )
                res = self.gemini_client.query_visual_target(route.raw_query, screen)

                if res.target_found and res.coordinates:
                    norm_x, norm_y = res.coordinates
                    abs_x, abs_y = screen.map_to_screen_coordinates(norm_x, norm_y)
                    logger.info("Pointing cursor to physical coordinates: (%d, %d)", abs_x, abs_y)
                    self.cursor_pointer.point_to(abs_x, abs_y)

                    # Memorize in the active app's profile to prevent future credit usage
                    if screen.process_name:
                        app_id = screen.process_name.lower().replace(".exe", "")
                        self.universal_engine.profile_mgr.record_interaction(
                            app_id=app_id,
                            trigger_phrase=route.raw_query,
                            relative_coords=(norm_x, norm_y)
                        )
                        logger.info("Permanently memorized interaction for [%s]: %s", app_id, route.raw_query)

                # Speak the explanation locally (0 tokens, $0.00 cost)
                if res.response_text:
                    self.speech_engine.speak(res.response_text)
                return res.response_text
            except ScreenSecurityViolation as sec_err:
                logger.warning("Screen indexing blocked by security shield: %s", sec_err)
                msg = "Visual capture is blocked to protect your private credentials."
                self.speech_engine.speak(msg)
                return f"[Security Blocked] {sec_err}"
            except Exception as exc:
                logger.error("Visual processing failed: %s", exc)
                return f"[Error] Screen indexing failed: {exc}"


        # Tier 1.5: Conversational Dialogue Fallback (No screenshot required)
        if route.target == RouteTarget.CONVERSATIONAL_FALLBACK or route.is_cloud_request:
            logger.info("Routing conversational query to Gemini...")
            try:
                answer = self.gemini_client.query_conversational(route.raw_query)
                self.speech_engine.speak(answer)
                return answer
            except Exception as exc:
                logger.error("Conversational query failed: %s", exc)
                return f"[Error] Conversational assistant failed: {exc}"

        return "No action taken."

