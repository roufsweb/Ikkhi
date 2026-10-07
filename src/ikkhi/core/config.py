"""
Configuration management system for Ikkhi using Pydantic Settings.
"""

import os
from pathlib import Path
from typing import Literal, Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class SystemSettings(BaseModel):
    name: str = "Ikkhi"
    debug: bool = True
    log_level: str = "INFO"
    storage_directory: str = "storage"


class NetworkSettings(BaseModel):
    proxy: str = "socks5://02:1234@27.147.152.33:5645"
    use_proxy_for_downloads: bool = True


class AudioSettings(BaseModel):
    activation_mode: Literal["both", "push_to_talk", "wake_word"] = "both"
    push_to_talk_key: str = "ctrl+alt+space"
    wake_word: str = "hey ikkhi"
    sample_rate: int = 16000
    whisper_model: str = "base.en"
    whisper_device: Literal["cuda", "cpu"] = "cuda"
    compute_type: Literal["float16", "int8_float16", "int8"] = "float16"
    input_device: Optional[int | str] = None
    tts_engine: Literal["neural", "sapi"] = "neural"
    tts_voice: str = "en-US-AvaNeural"
    tts_rate: str = "+0%"
    tts_pitch: str = "+0Hz"


class AITierSettings(BaseModel):
    enable_cloud_fallback: bool = True
    model_name: str = "gemini-2.5-flash"
    auto_select_model: bool = True
    max_output_tokens: int = 350
    temperature: float = 0.1
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_project_id: str = Field(default_factory=lambda: os.getenv("GEMINI_PROJECT_ID", ""))


class ScreenIndexingSettings(BaseModel):
    crop_active_window_only: bool = True
    max_image_dimension: int = 1024
    jpeg_quality: int = 80
    cache_ttl_seconds: int = 5


class PointerSettings(BaseModel):
    smooth_move_duration: float = 0.35
    highlight_circle_radius: int = 25
    highlight_duration_seconds: float = 1.5


class UniversalAutomationSettings(BaseModel):
    enabled: bool = True
    profiles_directory: str = "storage/profiles"
    uia_search_depth: int = 4
    auto_learn_interactions: bool = True
    max_cached_controls_per_app: int = 250


class AppConfig(BaseSettings):
    """Root configuration aggregator with YAML fallback and environment overrides."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    system: SystemSettings = Field(default_factory=SystemSettings)
    network: NetworkSettings = Field(default_factory=NetworkSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    ai_tier: AITierSettings = Field(default_factory=AITierSettings)
    screen_indexing: ScreenIndexingSettings = Field(default_factory=ScreenIndexingSettings)
    pointer: PointerSettings = Field(default_factory=PointerSettings)
    universal_automation: UniversalAutomationSettings = Field(default_factory=UniversalAutomationSettings)


    @classmethod
    def load_from_yaml(cls, yaml_path: Path | str = "config.yaml") -> "AppConfig":
        """Load configuration from a YAML file, overlaid with environment variables."""
        from ikkhi.core.paths import resolve_config_path
        p = resolve_config_path(yaml_path)
        if not p.is_file():
            return cls()

        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Overlay environment secrets for ai_tier if not explicitly set in YAML
        if "ai_tier" in data and isinstance(data["ai_tier"], dict):
            if not data["ai_tier"].get("gemini_api_key"):
                data["ai_tier"]["gemini_api_key"] = os.getenv("GEMINI_API_KEY", "")
            if not data["ai_tier"].get("gemini_project_id"):
                data["ai_tier"]["gemini_project_id"] = os.getenv("GEMINI_PROJECT_ID", "")

        return cls(**data)
