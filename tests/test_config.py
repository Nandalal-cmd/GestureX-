import pytest

from app.config import AppConfig


def test_default_configuration_is_valid() -> None:
    config = AppConfig()
    assert config.default_particles <= config.max_particles


def test_configuration_rejects_invalid_smoothing() -> None:
    with pytest.raises(ValueError, match="smoothing_factor"):
        AppConfig(smoothing_factor=1.0)


def test_configuration_rejects_invalid_effect_strength() -> None:
    with pytest.raises(ValueError, match="effect_strength"):
        AppConfig(effect_strength=1.5)
