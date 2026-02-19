"""Test configuration and settings management."""

import tempfile
from pathlib import Path

from ai_writer.config.settings import GenerationSettings, OllamaSettings, Settings


class TestOllamaSettings:
    """Test OllamaSettings dataclass."""

    def test_default_values(self):
        """Test default values are correct."""
        settings = OllamaSettings()
        assert settings.url == "http://localhost:11434"
        assert settings.timeout == 120
        assert settings.default_model is None

    def test_custom_values(self):
        """Test custom values can be set."""
        settings = OllamaSettings(
            url="http://custom:8080", timeout=60, default_model="llama2"
        )
        assert settings.url == "http://custom:8080"
        assert settings.timeout == 60
        assert settings.default_model == "llama2"


class TestGenerationSettings:
    """Test GenerationSettings dataclass."""

    def test_default_values(self):
        """Test default values are correct."""
        settings = GenerationSettings()
        assert settings.default_token_limit == 140
        assert settings.default_temperature == 0.7
        assert settings.min_token_limit == 10
        assert settings.max_token_limit == 2000


class TestSettings:
    """Test main Settings class."""

    def test_default_settings(self):
        """Test default settings creation."""
        settings = Settings()
        assert isinstance(settings.ollama, OllamaSettings)
        assert isinstance(settings.generation, GenerationSettings)
        assert settings.ui.default_theme == "light"

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_file = f.name

        try:
            # Create and save settings
            original_settings = Settings()
            original_settings.generation.default_temperature = 0.9
            original_settings.ollama.default_model = "test-model"
            original_settings.save(config_file)

            # Load settings from file
            loaded_settings = Settings.load(config_file)
            assert loaded_settings.generation.default_temperature == 0.9
            assert loaded_settings.ollama.default_model == "test-model"

        finally:
            Path(config_file).unlink(missing_ok=True)

    def test_invalid_config_file(self):
        """Test handling of invalid config file."""
        # Should not crash with non-existent file
        settings = Settings.load("nonexistent.json")
        assert isinstance(settings, Settings)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        settings = Settings()
        settings.generation.default_temperature = 0.8

        data = settings._to_dict()
        assert data["generation"]["default_temperature"] == 0.8
        assert "ollama" in data
        assert "ui" in data
        assert "file" in data
