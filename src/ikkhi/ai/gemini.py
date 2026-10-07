"""
Credit-optimized Google AI Studio (Gemini) client for visual grounding and conversational fallback.
Integrates ReasonedModelOrchestrator for dynamic model discovery, task-aware reasoned selection,
and resilient multi-model fallback execution.
"""

import re
import json
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List
from google.genai import types
from ikkhi.core.config import AITierSettings
from ikkhi.vision.indexer import IndexedScreen
from ikkhi.ai.router_model import ReasonedModelOrchestrator, ModelInfo

logger = logging.getLogger("ikkhi.ai.gemini")


@dataclass
class VisualQueryResult:
    target_found: bool
    coordinates: Optional[Tuple[float, float]]  # (norm_x, norm_y) 0.0 to 1.0 within window crop
    response_text: str
    used_model: Optional[str] = None
    reasoning: Optional[str] = None


class GeminiVisualClient:
    """Client for on-demand visual queries and conversational fallback."""

    SYSTEM_INSTRUCTION = (
        "You are Ikkhi's visual assistant. The user provides an image crop of an application window "
        "and asks a question about the UI or where a control is located.\n"
        "Respond strictly with a JSON object adhering to this schema:\n"
        "{\n"
        '  "target_found": true/false,\n'
        '  "normalized_x": float between 0.0 and 1.0 (relative horizontal position within the provided image),\n'
        '  "normalized_y": float between 0.0 and 1.0 (relative vertical position within the provided image),\n'
        '  "explanation": "Concise 1-sentence answer to the user"\n'
        "}\n"
        "If no specific element is targeted, set target_found to false and leave coordinates null."
    )

    CONVERSATIONAL_INSTRUCTION = (
        "You are Ikkhi, a fast, lightweight, voice-controlled Windows desktop assistant. "
        "Answer the user conversationally, concisely (1-2 sentences maximum), directly, and naturally. "
        "Do not use markdown formatting, asterisks, bullet points, or code blocks, as your output is read aloud via speech synthesis."
    )

    def __init__(self, settings: AITierSettings) -> None:
        self.settings = settings
        self.orchestrator = ReasonedModelOrchestrator(api_key=settings.gemini_api_key)

    @property
    def client(self):
        return self.orchestrator.client

    def get_available_models(self, force_refresh: bool = False) -> List[str]:
        """Returns list of active generative model IDs discovered on Google AI Studio."""
        models = self.orchestrator.list_available_models(force_refresh=force_refresh)
        return [m.name for m in models]

    def resolve_active_model(self) -> str:
        """Resolves the preferred or reasoned model."""
        avail = self.get_available_models()
        if self.settings.model_name and (not avail or self.settings.model_name in avail):
            return self.settings.model_name
        chosen, _, _ = self.orchestrator.select_reasoned_model(
            user_prompt="",
            has_image=True,
            preferred_model=self.settings.model_name
        )
        return chosen

    def query_conversational(self, user_prompt: str) -> str:
        """Processes conversational and general user queries without screen capture."""
        if not self.orchestrator.client:
            return "Google AI Studio API key not configured in .env."

        try:
            response, used_model, reasoning = self.orchestrator.generate_with_fallback(
                contents=[user_prompt],
                system_instruction=self.CONVERSATIONAL_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=150,
                user_prompt=user_prompt,
                has_image=False,
                preferred_model=self.settings.model_name
            )
            raw_text = response.text.strip() if hasattr(response, "text") and response.text else ""
            # Clean markdown formatting so TTS sounds natural
            cleaned = re.sub(r"[*#_`]", "", raw_text).strip()
            return cleaned if cleaned else "I am here and listening."
        except Exception as exc:
            logger.error("Conversational query error: %s", exc)
            return "I am having trouble answering right now."

    def query_visual_target(self, user_prompt: str, screen: IndexedScreen) -> VisualQueryResult:
        """Sends compressed screen crop to Gemini with strict token limits, task reasoning, and fallback."""
        if not self.orchestrator.client:
            return VisualQueryResult(
                target_found=False,
                coordinates=None,
                response_text="Google AI Studio API key not configured in .env."
            )

        try:
            image_part = types.Part.from_bytes(
                data=screen.image_bytes,
                mime_type=screen.mime_type
            )

            response, used_model, reasoning = self.orchestrator.generate_with_fallback(
                contents=[image_part, user_prompt],
                system_instruction=self.SYSTEM_INSTRUCTION,
                temperature=self.settings.temperature,
                max_output_tokens=self.settings.max_output_tokens,
                response_mime_type="application/json",
                user_prompt=user_prompt,
                has_image=True,
                preferred_model=self.settings.model_name
            )

            raw_text = response.text.strip() if hasattr(response, "text") and response.text else "{}"
            # Extract JSON substring if surrounded by fences or text
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            clean_json = json_match.group(0) if json_match else raw_text

            try:
                result_json = json.loads(clean_json)
            except Exception:
                result_json = {"target_found": False, "explanation": raw_text.strip()}

            target_found = result_json.get("target_found", False)
            coords = None
            if target_found and "normalized_x" in result_json and "normalized_y" in result_json:
                coords = (float(result_json["normalized_x"]), float(result_json["normalized_y"]))

            explanation = result_json.get("explanation", "").strip()
            if not explanation:
                explanation = "Element located on screen." if target_found else "I could not locate that element on screen."

            return VisualQueryResult(
                target_found=target_found,
                coordinates=coords,
                response_text=explanation,
                used_model=used_model,
                reasoning=reasoning
            )
        except Exception as exc:
            logger.error("Visual processing failed: %s", exc)
            return VisualQueryResult(
                target_found=False,
                coordinates=None,
                response_text="I could not find that control on your screen."
            )
