"""Flame emission that reacts to a closed hand."""

from __future__ import annotations

import logging
from random import Random

from app.config import AppConfig
from particles.particle_system import ParticleSystem
from utils.geometry import Point

EMISSION_INTERVAL = 0.02
EMIT_PER_TICK = 2
RISE_SPEED = 0.5
LIFT = 0.08
SPREAD = 0.06
MIN_SIZE = 3.0
MAX_SIZE = 7.0
FLAME_DRAG = 0.9
COLOR_LIFETIME = 0.75
CEILING = 0.02
COLOR_STOPS = (
    (1.00, (255, 246, 200)),
    (0.55, (255, 168, 40)),
    (0.25, (226, 72, 12)),
    (0.00, (70, 14, 6)),
)


class FireEffect:
    """Emit upward-moving flame particles at the hand while a fist is held."""

    def __init__(self, config: AppConfig, *, rng: Random | None = None) -> None:
        self.config = config
        self._rng = rng if rng is not None else Random()
        self._logger = logging.getLogger(__name__)
        self._accumulator = 0.0
        self.source: Point | None = None

    def set_source(self, point: Point | None) -> None:
        """Point the fire at a hand position, or switch it off with None."""
        if point is None:
            self._accumulator = 0.0
        self.source = point

    def update(self, system: ParticleSystem, dt: float) -> None:
        """Emit flame at the current source and keep existing embers rising."""
        if self.source is None:
            return
        self._accumulator += dt
        while self._accumulator >= EMISSION_INTERVAL:
            self._accumulator -= EMISSION_INTERVAL
            self._emit(system, self.source)
        self._lift(system, dt)

    def _emit(self, system: ParticleSystem, source: Point) -> None:
        """Start a few flame particles near the hand and give them an upward push."""
        for particle in system.emit((source[0], source[1]), count=EMIT_PER_TICK, speed=SPREAD):
            particle.vy -= RISE_SPEED * self._rng.uniform(0.6, 1.0)
            particle.vx *= 0.5
            particle.size = self._rng.uniform(MIN_SIZE, MAX_SIZE)
            particle.drag = FLAME_DRAG
            particle.life = min(particle.life, COLOR_LIFETIME)

    def _lift(self, system: ParticleSystem, dt: float) -> None:
        """Drift embers upward, then damp and stop them at the top of the frame."""
        for particle in system.particles:
            if not particle.is_alive:
                continue
            if particle.y <= CEILING:
                particle.y = CEILING
                if particle.vy < 0.0:
                    particle.vy *= -0.2
            else:
                particle.vy -= LIFT * dt


def flame_color(life_ratio: float) -> tuple[int, int, int]:
    """Map a particle's remaining lifetime to a hot-to-cool flame color."""
    clamped = min(1.0, max(0.0, life_ratio))
    for index in range(len(COLOR_STOPS) - 1):
        high_ratio, high_color = COLOR_STOPS[index]
        low_ratio, low_color = COLOR_STOPS[index + 1]
        if low_ratio <= clamped <= high_ratio:
            span = high_ratio - low_ratio
            blend = 0.0 if span <= 0.0 else (clamped - low_ratio) / span
            return (
                round(low_color[0] + (high_color[0] - low_color[0]) * blend),
                round(low_color[1] + (high_color[1] - low_color[1]) * blend),
                round(low_color[2] + (high_color[2] - low_color[2]) * blend),
            )
    return COLOR_STOPS[-1][1]