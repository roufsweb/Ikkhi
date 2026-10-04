"""
Unit tests for the Ikkhi configuration module.
"""

from ikkhi.core.config import AppConfig


def test_default_config_instantiation():
    """Verify that AppConfig instantiates with valid defaults."""
    config = AppConfig()
    assert config.system.name == "Ikkhi"
    assert config.audio.whisper_model == "base.en"
    assert config.screen_indexing.crop_active_window_only is True
    assert config.screen_indexing.max_image_dimension == 1024


def test_load_from_yaml(tmp_path):
    """Verify that YAML configuration loading applies overrides correctly."""
    yaml_content = """
system:
  name: "IkkhiTest"
  debug: false
audio:
  whisper_model: "small.en"
"""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(yaml_content, encoding="utf-8")

    config = AppConfig.load_from_yaml(config_file)
    assert config.system.name == "IkkhiTest"
    assert config.system.debug is False
    assert config.audio.whisper_model == "small.en"
