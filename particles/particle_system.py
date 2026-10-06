import random

from particles.particle import Particle


class ParticleSystem:
    def __init__(self, max_particles: int = 2000, target: int = 800):
        self.max_particles = max_particles
        self.target = target
        self._pool = [Particle() for _ in range(max_particles)]

    @property
    def alive_count(self) -> int:
        return sum(1 for p in self._pool if p.alive)

    def spawn_one(self, x, y, **kwargs):
        for p in self._pool:
            if not p.alive:
                p.spawn(x, y, **kwargs)
                return p
        return None

    def spawn_around(self, cx, cy, count, radius=40, **kwargs):
        import math
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            r = random.uniform(0, radius)
            self.spawn_one(cx + math.cos(angle) * r, cy + math.sin(angle) * r, **kwargs)

    def fill_to_target(self, width, height, color=None):
        missing = self.target - self.alive_count
        for _ in range(max(0, missing)):
            self.spawn_one(random.uniform(0, width), random.uniform(0, height), color=color)

    def update(self, dt, drag=0.985):
        for p in self._pool:
            if p.alive:
                p.update(dt, drag=drag)

    def alive_particles(self):
        return (p for p in self._pool if p.alive)

    def clear(self):
        for p in self._pool:
            p.alive = False
