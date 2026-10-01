"""Fixed-capacity particle pool that reuses particles instead of reallocating them."""

from __future__ import annotations

from math import cos, sin, tau
from random import Random

from app.config import AppConfig
from particles.particle import Particle
from particles.physics import apply_attraction, apply_drag, apply_repulsion, step
from utils.geometry import Point

Bounds = tuple[float, float, float, float]
MIN_SIZE = 1.5
MAX_SIZE = 4.5
MIN_LIFETIME = 2.0
MAX_LIFETIME = 6.0
SPAWN_SPEED = 0.05


def _life_ratio(particle: Particle) -> float:
    return particle.life_ratio


class ParticleSystem:
    """Own a reusable pool of particles and the forces that gestures apply to them.

    The system never touches the camera or the renderer: callers hand it target
    points and read the pool back for drawing. The population only changes through
    :meth:`emit` and :meth:`fill`, unless ``auto_fill`` keeps it topped up.
    """

    def __init__(
        self,
        config: AppConfig,
        *,
        count: int | None = None,
        bounds: Bounds | None = None,
        rng: Random | None = None,
        auto_fill: bool = False,
    ) -> None:
        resolved = config.default_particles if count is None else count
        if not 1 <= resolved <= config.max_particles:
            raise ValueError("count must be between 1 and config.max_particles")
        self._config = config
        self._rng = rng if rng is not None else Random()
        self._bounds = bounds
        self._auto_fill = auto_fill
        self._cursor = 0
        self._particles = [Particle() for _ in range(resolved)]
        self._alive = 0
        for particle in self._particles:
            self._respawn(particle)
        self._alive = self._count_alive()

    @property
    def particles(self) -> list[Particle]:
        """Return the pool for iteration; callers must not add or remove entries."""
        return self._particles

    @property
    def capacity(self) -> int:
        """Return the maximum number of particles this system will ever hold."""
        return len(self._particles)

    @property
    def active_count(self) -> int:
        """Return how many particles currently have remaining lifetime."""
        return self._alive

    def update(self, dt: float) -> None:
        """Advance every live particle by dt seconds, applying drag and topping up if enabled."""
        for particle in self._particles:
            if particle.is_alive:
                apply_drag(particle, dt)
                step(particle, dt)
        if self._auto_fill:
            self._revive_expired()
        self._alive = self._count_alive()

    def attract(self, point: Point, strength: float | None = None) -> None:
        """Pull every live particle toward a point."""
        factor = self._resolve(strength)
        for particle in self._particles:
            if particle.is_alive:
                apply_attraction(particle, point, factor)

    def repel(self, point: Point, strength: float | None = None) -> None:
        """Push every live particle away from a point."""
        factor = self._resolve(strength)
        for particle in self._particles:
            if particle.is_alive:
                apply_repulsion(particle, point, factor)

    def impulse(self, dx: float, dy: float, strength: float | None = None) -> None:
        """Add a one-off directional velocity, used for swipe reactions."""
        factor = self._resolve(strength)
        for particle in self._particles:
            if particle.is_alive:
                particle.vx += dx * factor
                particle.vy += dy * factor

    def emit(self, point: Point, *, count: int = 1, speed: float = SPAWN_SPEED) -> int:
        """Start up to count particles near a point, returning how many were started."""
        emitted = 0
        for _ in range(min(count, self.capacity)):
            particle = self._take_slot()
            expired = not particle.is_alive
            angle = self._rng.uniform(0.0, tau)
            direction_x, direction_y = cos(angle) * speed, sin(angle) * speed
            particle.spawn(
                point[0] + direction_x,
                point[1] + direction_y,
                direction_x * self._rng.uniform(0.5, 1.5),
                direction_y * self._rng.uniform(0.5, 1.5),
                size=self._random_size(),
                lifetime=self._random_lifetime(),
            )
            self._alive += int(expired)
            emitted += 1
        return emitted

    def fill(self) -> int:
        """Revive every expired particle at a random position, returning how many started."""
        revived = self._revive_expired()
        self._alive += revived
        return revived

    def _revive_expired(self) -> int:
        revived = 0
        for particle in self._particles:
            if not particle.is_alive:
                self._respawn(particle)
                revived += 1
        return revived

    def _take_slot(self) -> Particle:
        """Return an expired particle, or the one closest to expiry when the pool is full."""
        total = len(self._particles)
        for offset in range(total):
            index = (self._cursor + offset) % total
            particle = self._particles[index]
            if not particle.is_alive:
                self._cursor = (index + 1) % total
                return particle
        return min(self._particles, key=_life_ratio)

    def _count_alive(self) -> int:
        alive = 0
        for particle in self._particles:
            if particle.is_alive:
                alive += 1
        return alive

    def _respawn(self, particle: Particle) -> None:
        """Restart a particle at a random position, used for the initial fill."""
        x, y = self._random_position()
        particle.spawn(
            x,
            y,
            self._rng.uniform(-SPAWN_SPEED, SPAWN_SPEED),
            self._rng.uniform(-SPAWN_SPEED, SPAWN_SPEED),
            size=self._random_size(),
            lifetime=self._random_lifetime(),
        )

    def _random_position(self) -> Point:
        if self._bounds is None:
            return (0.0, 0.0)
        x, y, width, height = self._bounds
        return (self._rng.uniform(x, x + width), self._rng.uniform(y, y + height))

    def _random_size(self) -> float:
        return self._rng.uniform(MIN_SIZE, MAX_SIZE)

    def _random_lifetime(self) -> float:
        return self._rng.uniform(MIN_LIFETIME, MAX_LIFETIME)

    def _resolve(self, strength: float | None) -> float:
        return self._config.effect_strength if strength is None else strength