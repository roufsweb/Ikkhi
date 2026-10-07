"""
Unit tests for dynamic Gemini model verification, reasoned selection, and fallback.
"""

from unittest.mock import MagicMock
from ikkhi.core.config import AITierSettings
from ikkhi.ai.gemini import GeminiVisualClient
from ikkhi.ai.router_model import ReasonedModelOrchestrator, ModelInfo


def test_gemini_model_resolution_exact_match():
    settings = AITierSettings(model_name="gemini-2.5-flash", gemini_api_key="mock_key")
    client = GeminiVisualClient(settings)
    client.get_available_models = MagicMock(return_value=["gemini-2.5-flash", "gemini-2.5-pro"])

    resolved = client.resolve_active_model()
    assert resolved == "gemini-2.5-flash"


def test_gemini_model_resolution_no_key():
    settings = AITierSettings(model_name="gemini-2.5-flash", gemini_api_key="")
    client = GeminiVisualClient(settings)
    resolved = client.resolve_active_model()
    assert resolved == "gemini-2.5-flash"


def test_reasoned_selection_visual_query():
    orch = ReasonedModelOrchestrator("mock_key")
    orch.list_available_models = MagicMock(return_value=[
        ModelInfo(name="gemini-2.5-flash", display_name="Flash", description="", supports_vision=True, is_flash=True, is_pro=False),
        ModelInfo(name="gemini-2.5-pro", display_name="Pro", description="", supports_vision=True, is_flash=False, is_pro=True),
        ModelInfo(name="gemini-flash-latest", display_name="Latest", description="", supports_vision=True, is_flash=True, is_pro=False),
    ])

    chosen, reasoning, fallbacks = orch.select_reasoned_model(
        user_prompt="Click the save button",
        has_image=True
    )
    assert chosen == "gemini-2.5-flash"
    assert "visual" in reasoning.lower()
    assert "gemini-flash-latest" in fallbacks or "gemini-2.5-pro" in fallbacks


def test_reasoned_selection_complex_query():
    orch = ReasonedModelOrchestrator("mock_key")
    orch.list_available_models = MagicMock(return_value=[
        ModelInfo(name="gemini-2.5-pro", display_name="Pro", description="", supports_vision=True, is_flash=False, is_pro=True),
        ModelInfo(name="gemini-2.5-flash", display_name="Flash", description="", supports_vision=True, is_flash=True, is_pro=False),
    ])

    chosen, reasoning, fallbacks = orch.select_reasoned_model(
        user_prompt="Why and how does this async deadlock occur? Debug and analyze",
        has_image=False
    )
    assert chosen == "gemini-2.5-pro"
    assert "complex" in reasoning.lower() or "analytical" in reasoning.lower()
