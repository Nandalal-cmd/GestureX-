"""Reusable particle state for the GestureFX particle system."""

from __future__ import annotations

from utils.geometry import Point

DEFAULT_SIZE = 3.0
DEFAULT_LIFETIME = 4.0
DEFAULT_DRAG = 1.2


class Particle:
    """A single particle whose fields are mutated in place so objects can be reused."""

    __slots__ = ("x", "y", "vx", "vy", "size", "life", "max_life", "opacity", "drag")

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        vx: float = 0.0,
        vy: float = 0.0,
        *,
        size: float = DEFAULT_SIZE,
        lifetime: float = DEFAULT_LIFETIME,
        drag: float = DEFAULT_DRAG,
    ) -> None:
        self.spawn(x, y, vx, vy, size=size, lifetime=lifetime, drag=drag)

    def spawn(
        self,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
        *,
        size: float = DEFAULT_SIZE,
        lifetime: float = DEFAULT_LIFETIME,
        drag: float = DEFAULT_DRAG,
    ) -> None:
        """(Re)initialize this particle in place, resetting its lifetime and opacity."""
        if lifetime <= 0.0:
            raise ValueError("lifetime must be positive")
        if drag < 0.0:
            raise ValueError("drag must not be negative")
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.drag = drag
        self.max_life = lifetime
        self.life = lifetime
        self.opacity = 1.0

    @property
    def is_alive(self) -> bool:
        """Return True while the particle still has remaining lifetime."""
        return self.life > 0.0

    @property
    def life_ratio(self) -> float:
        """Return the remaining lifetime as a fraction between 0.0 and 1.0."""
        return max(0.0, self.life / self.max_life)

    @property
    def position(self) -> Point:
        """Return the current position as a point."""
        return (self.x, self.y)