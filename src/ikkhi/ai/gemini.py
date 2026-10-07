"""
Credit-optimized Google AI Studio (Gemini) client for visual grounding and conversational fallback.
Integrates ReasonedModelOrchestrator for dynamic model discovery, task-aware reasoned selection,
and resilient multi-model fallback execution.
"""

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
    """Client for on-demand visual queries, strictly budgeted for token conservation."""

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
        chosen, _, _ = self.orchestrator.select_reasoned_model(
            user_prompt="",
            has_image=True,
            preferred_model=self.settings.model_name
        )
        return chosen

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

            result_json = json.loads(response.text)
            target_found = result_json.get("target_found", False)
            coords = None
            if target_found and "normalized_x" in result_json and "normalized_y" in result_json:
                coords = (float(result_json["normalized_x"]), float(result_json["normalized_y"]))

            return VisualQueryResult(
                target_found=target_found,
                coordinates=coords,
                response_text=result_json.get("explanation", ""),
                used_model=used_model,
                reasoning=reasoning
            )
        except Exception as exc:
            return VisualQueryResult(
                target_found=False,
                coordinates=None,
                response_text=f"Visual query failed: {exc}"
            )
