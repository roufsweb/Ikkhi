"""
Credit-optimized Google AI Studio (Gemini) client for visual grounding and conversational fallback.
"""

import json
from dataclasses import dataclass
from typing import Optional, Tuple
from google import genai
from google.genai import types
from ikkhi.core.config import AITierSettings
from ikkhi.vision.indexer import IndexedScreen


@dataclass
class VisualQueryResult:
    target_found: bool
    coordinates: Optional[Tuple[float, float]] # (norm_x, norm_y) 0.0 to 1.0 within window crop
    response_text: str


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
        self.client: Optional[genai.Client] = None
        if self.settings.gemini_api_key:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)

    def query_visual_target(self, user_prompt: str, screen: IndexedScreen) -> VisualQueryResult:
        """Sends compressed screen crop to Gemini with strict token limits."""
        if not self.client:
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
            response = self.client.models.generate_content(
                model=self.settings.model_name,
                contents=[image_part, user_prompt],
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION,
                    temperature=self.settings.temperature,
                    max_output_tokens=self.settings.max_output_tokens,
                    response_mime_type="application/json"
                )
            )

            result_json = json.loads(response.text)
            target_found = result_json.get("target_found", False)
            coords = None
            if target_found and "normalized_x" in result_json and "normalized_y" in result_json:
                coords = (float(result_json["normalized_x"]), float(result_json["normalized_y"]))

            return VisualQueryResult(
                target_found=target_found,
                coordinates=coords,
                response_text=result_json.get("explanation", "")
            )
        except Exception as exc:
            return VisualQueryResult(
                target_found=False,
                coordinates=None,
                response_text=f"Visual query failed: {exc}"
            )
