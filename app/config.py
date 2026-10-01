"""Central application configuration for GestureFX."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings shared by application modules."""

    camera_index: int = 0
    camera_width: int = 1280
    camera_height: int = 720
    max_particles: int = 2000
    default_particles: int = 800
    gesture_sensitivity: float = 0.5
    smoothing_factor: float = 0.65
    trail_length: int = 20
    effect_strength: float = 1.0
    target_fps: int = 60

    def __post_init__(self) -> None:
        if not 1 <= self.default_particles <= self.max_particles:
            raise ValueError("default_particles must be between 1 and max_particles")
        if not 0.0 <= self.gesture_sensitivity <= 1.0:
            raise ValueError("gesture_sensitivity must be between 0.0 and 1.0")
        if not 0.0 <= self.smoothing_factor < 1.0:
            raise ValueError("smoothing_factor must be between 0.0 and 1.0")
        if not 0.0 <= self.effect_strength <= 1.0:
            raise ValueError("effect_strength must be between 0.0 and 1.0")
        if self.trail_length < 1 or self.target_fps < 1:
            raise ValueError("trail_length and target_fps must be positive")
