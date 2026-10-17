import math

import pygame


class LaserSystem:
    """Projectile lasers fired from a pointing hand; pierce asteroids."""

    def __init__(self, speed: float = 1500.0, cooldown: float = 0.12,
                 life: float = 0.9):
        self.speed = speed
        self.cooldown = cooldown
        self.life = life
        self.shots = []
        self._last = -1e9
        self.heat = 0.0
        self.heat_per_shot = 0.18
        self.cool_rate = 0.6
        self.overheat = False

    def reset(self):
        self.shots = []
        self._last = -1e9

    def fire(self, origin, angle: float, now: float):
        if self.overheat:
            return False
        if now - self._last < self.cooldown:
            return False
        self._last = now
        self.heat = min(1.0, self.heat + self.heat_per_shot)
        if self.heat >= 1.0:
            self.overheat = True
        dx = math.cos(angle)
        dy = math.sin(angle)
        self.shots.append({
            "x": float(origin[0]),
            "y": float(origin[1]),
            "vx": dx * self.speed,
            "vy": dy * self.speed,
            "age": 0.0,
            "heat": self.heat,
        })
        return True

    def update(self, dt: float):
        self.heat = max(0.0, self.heat - self.cool_rate * dt)
        if self.overheat and self.heat < 0.25:
            self.overheat = False
        for s in self.shots:
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["age"] += dt
        self.shots = [s for s in self.shots if s["age"] < self.life]

    def draw(self, surface):
        for s in self.shots:
            x, y = s["x"], s["y"]
            tail = (x - s["vx"] * 0.045, y - s["vy"] * 0.045)
            k = max(0.0, min(1.0, s.get("heat", 0.0)))
            core = (230, int(250 - 90 * k), int(255 - 205 * k))
            halo = (int(90 + 165 * k), int(220 - 120 * k), int(255 - 235 * k))
            line = (int(120 + 135 * k), int(230 - 130 * k), int(255 - 220 * k))
            d = 26
            glow = pygame.Surface((d, d), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*halo, int(90 + 60 * k)), (d // 2, d // 2), d // 2)
            pygame.draw.circle(glow, (*core, 220), (d // 2, d // 2), 5)
            surface.blit(glow, (int(x) - d // 2, int(y) - d // 2))
            pygame.draw.line(surface, line,
                             (int(tail[0]), int(tail[1])), (int(x), int(y)), 2)