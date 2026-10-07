"""
Dynamic Gemini Model Discovery, Reasoned Selection & Resilient Fallback Engine.
Queries Google AI Studio to inspect all active models on the account, selects the optimal
model with transparent reasoning based on user input (vision vs deep logic vs fast speed),
and automatically walks a fallback hierarchy if a model encounters rate limits or errors.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple
from google import genai
from google.genai import types

logger = logging.getLogger("ikkhi.ai.router_model")


@dataclass
class ModelInfo:
    name: str
    display_name: str
    description: str
    supports_vision: bool
    is_flash: bool
    is_pro: bool


class ReasonedModelOrchestrator:
    """
    Intelligent Model Selector and Fallback Manager.
    - Discovers active models from the user's Google AI Studio API key
    - Formulates transparent reasoning for model selection based on prompt characteristics
    - Orchestrates seamless multi-model fallback execution
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client: Optional[genai.Client] = None
        self._cached_models: Optional[List[ModelInfo]] = None

        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                logger.error("Failed to initialize Google GenAI Client: %s", exc)

    def list_available_models(self, force_refresh: bool = False) -> List[ModelInfo]:
        """
        Discovers all available generative models on the user's Google AI Studio account.
        Filters out embedding-only models and parses capabilities.
        """
        if self._cached_models is not None and not force_refresh:
            return self._cached_models

        if not self.client:
            return []

        try:
            raw_models = list(self.client.models.list())
            catalog: List[ModelInfo] = []

            for m in raw_models:
                m_name = (m.name or "").replace("models/", "")
                # Skip embedding and specialized non-content models
                if "embedding" in m_name or "tts" in m_name or "transcribe" in m_name or "image" in m_name:
                    continue

                display_name = getattr(m, "display_name", m_name)
                desc = getattr(m, "description", "")
                is_flash = "flash" in m_name.lower()
                is_pro = "pro" in m_name.lower()
                supports_vision = is_flash or is_pro or "gemini" in m_name.lower()

                catalog.append(ModelInfo(
                    name=m_name,
                    display_name=display_name,
                    description=desc,
                    supports_vision=supports_vision,
                    is_flash=is_flash,
                    is_pro=is_pro
                ))

            self._cached_models = catalog
            logger.info("Discovered %d active generative Gemini models.", len(catalog))
            return catalog
        except Exception as exc:
            logger.warning("Failed to list models from Gemini API: %s", exc)
            return []

    def select_reasoned_model(
        self,
        user_prompt: str,
        has_image: bool = False,
        preferred_model: Optional[str] = None
    ) -> Tuple[str, str, List[str]]:
        """
        Evaluates user input and returns (chosen_model, reasoning, fallback_chain).
        """
        available = [m.name for m in self.list_available_models()]
        clean_pref = preferred_model.replace("models/", "") if preferred_model else None

        # Determine task type
        is_complex = any(k in user_prompt.lower() for k in [
            "why", "how", "debug", "analyze", "explain code", "refactor", "diagnose", "script", "plan"
        ])

        # Formulate reasoning and prioritize candidate chain
        if has_image:
            # Case 1: Visual / UI Grounding Task
            priority = [
                "gemini-3.8-flash",
                "gemini-3.5-flash",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash",
                "gemini-flash-latest",
                "gemini-2.5-pro",
                "gemini-pro-latest",
            ]
            task_desc = "Multimodal visual screen grounding (requires high-speed spatial coordinate detection)."
        elif is_complex:
            # Case 2: Deep Analysis / Troubleshooting
            priority = [
                "gemini-2.5-pro",
                "gemini-pro-latest",
                "gemini-3.8-flash",
                "gemini-3.5-flash",
            ]
            task_desc = "Complex analytical and diagnostic reasoning (requires deep multi-step logic)."
        else:
            # Case 3: Fast conversational or utility query
            priority = [
                "gemini-3.8-flash",
                "gemini-3.5-flash",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash",
                "gemini-flash-latest",
            ]
            task_desc = "Fast interactive command assistance (optimized for minimal latency and high responsiveness)."

        # Filter candidates by what's actually available on this API key
        if available:
            valid_candidates = [c for c in priority if c in available]
            # Add any other available flash/pro models as secondary fallbacks
            for a in available:
                if a not in valid_candidates:
                    valid_candidates.append(a)
        else:
            valid_candidates = priority

        # If user explicitly preferred a model and it's valid, put it first
        if clean_pref and (not available or clean_pref in available):
            if clean_pref in valid_candidates:
                valid_candidates.remove(clean_pref)
            valid_candidates.insert(0, clean_pref)
            reasoning = f"User preferred model '{clean_pref}' is active and selected for {task_desc}"
        else:
            primary = valid_candidates[0] if valid_candidates else "gemini-2.5-flash"
            reasoning = f"Reasoned selection: '{primary}' chosen for {task_desc} (Confidence: High)"

        chosen = valid_candidates[0] if valid_candidates else "gemini-2.5-flash"
        fallback_chain = valid_candidates[1:4]  # Top 3 fallbacks

        logger.info("[MODEL_REASONING] %s | Fallback Chain: %s", reasoning, fallback_chain)
        return chosen, reasoning, fallback_chain

    def generate_with_fallback(
        self,
        contents: list,
        system_instruction: str,
        temperature: float = 0.1,
        max_output_tokens: int = 350,
        response_mime_type: Optional[str] = None,
        user_prompt: str = "",
        has_image: bool = False,
        preferred_model: Optional[str] = None
    ) -> Tuple[types.GenerateContentResponse, str, str]:
        """
        Executes content generation with reasoned model selection and automated fallback chain.
        Returns: (response, used_model_name, reasoning)
        """
        if not self.client:
            raise RuntimeError("Gemini Client is not configured with an API key.")

        chosen_model, reasoning, fallbacks = self.select_reasoned_model(
            user_prompt=user_prompt,
            has_image=has_image,
            preferred_model=preferred_model
        )

        models_to_try = [chosen_model] + fallbacks
        last_exception = None

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type
        )

        for attempt_idx, model_name in enumerate(models_to_try):
            try:
                logger.info("Executing generation with model: '%s' (attempt %d/%d)", model_name, attempt_idx + 1, len(models_to_try))
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
                return response, model_name, reasoning
            except Exception as exc:
                last_exception = exc
                logger.warning(
                    "[AI_FALLBACK] Model '%s' encountered error: %s. Advancing fallback chain...",
                    model_name,
                    exc
                )

        raise RuntimeError(f"All models in fallback chain failed. Last error: {last_exception}")
