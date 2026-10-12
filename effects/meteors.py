import math
import random

import pygame


class MeteorShower:
    """Periodic meteor streaks flying across the scene; shootable for points."""

    def __init__(self, interval_min: float = 18.0, interval_max: float = 30.0,
                 first_delay: float = 15.0, burst: int = 7, speed: float = 900.0):
        self.interval_min = interval_min
        self.interval_max = interval_max
        self.first_delay = first_delay
        self.burst = burst
        self.speed = speed
        self.meteors = []
        self.next_shower = first_delay
        self.active = 0.0
        self.just_started = False
        self.t = 0.0

    def _spawn_shower(self, width, height):
        from_side = random.randint(0, 3)
        heading = random.uniform(0, math.tau)
        sx = sy = 0.0
        if from_side == 0:
            sx = random.uniform(0, width)
            sy = -20
        elif from_side == 1:
            sx = random.uniform(0, width)
            sy = height + 20
        elif from_side == 2:
            sx = -20
            sy = random.uniform(0, height)
        else:
            sx = width + 20
            sy = random.uniform(0, height)
        for _ in range(self.burst):
            angle = heading + random.uniform(-0.18, 0.18)
            sp = self.speed * random.uniform(0.8, 1.25)
            self.meteors.append({
                "x": sx + random.uniform(-40, 40),
                "y": sy + random.uniform(-40, 40),
                "vx": math.cos(angle) * sp,
                "vy": math.sin(angle) * sp,
                "age": 0.0,
                "life": random.uniform(0.7, 1.1),
                "size": random.uniform(2.0, 4.5),
            })
        self.active = 3.0

    def update(self, dt, width=1280, height=720):
        self.t += dt
        self.next_shower -= dt
        if self.next_shower <= 0:
            self._spawn_shower(width, height)
            self.next_shower = random.uniform(self.interval_min, self.interval_max)
        self.just_started = True
        if self.active > 0:
            self.active -= dt
        for m in self.meteors:
            m["x"] += m["vx"] * dt
            m["y"] += m["vy"] * dt
            m["age"] += dt
        self.meteors = [m for m in self.meteors
                        if m["age"] < m["life"] and -60 < m["x"] < width + 60
                        and -60 < m["y"] < height + 60]

    def hit(self, pos, radius: float = 7.0):
        removed = []
        for m in self.meteors:
            if math.hypot(m["x"] - pos[0], m["y"] - pos[1]) <= m["size"] + radius:
                removed.append(m)
        for m in removed:
            self.meteors.remove(m)
        return removed

    def draw(self, surface):
        for m in self.meteors:
            tail = (m["x"] - m["vx"] * 0.05, m["y"] - m["vy"] * 0.05)
            fade = 1.0 - m["age"] / m["life"]
            col = (min(255, int(140 + 115 * fade)), 160, 200)
            pygame.draw.line(surface, col,
                             (int(tail[0]), int(tail[1])),
                             (int(m["x"]), int(m["y"])), max(1, int(m["size"])))
            d = int(18 * m["size"] * fade) + 6
            glow = pygame.Surface((d, d), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 190, 120, int(70 * fade)),
                               (d // 2, d // 2), d // 2)
            pygame.draw.circle(glow, (255, 225, 190, int(230 * fade)),
                               (d // 2, d // 2), max(1, int(m["size"])))
            surface.blit(glow, (int(m["x"]) - d // 2, int(m["y"]) - d // 2))