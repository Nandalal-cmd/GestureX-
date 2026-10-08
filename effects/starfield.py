import math
import random

import pygame


class Starfield:
    """Layered deep-space background: parallax stars, twinkle, nebula and
    occasional shooting stars."""

    LAYERS = (
        # count, size range, brightness range, twinkle speed, parallax factor
        (140, (1, 1), (60, 130), 0.7, 0.015),
        (70, (1, 2), (120, 190), 1.1, 0.035),
        (30, (2, 3), (180, 255), 1.6, 0.070),
    )
    SHOOT_INTERVAL = (4.0, 9.0)
    SHOOT_LIFE = 1.1

    def __init__(self, width: int, height: int, seed: int = 11):
        self.width = width
        self.height = height
        rng = random.Random(seed)
        self.layers = []
        for count, sizes, bright, speed, parallax in self.LAYERS:
            stars = []
            for _ in range(count):
                stars.append({
                    "x": rng.uniform(0, width),
                    "y": rng.uniform(0, height),
                    "size": rng.randint(*sizes),
                    "bright": rng.randint(*bright),
                    "phase": rng.uniform(0, math.tau),
                    "speed": speed * rng.uniform(0.7, 1.4),
                })
            self.layers.append({"stars": stars, "parallax": parallax})

        self.nebulae = self._build_nebulae(rng)
        self.shoot = None
        self.next_shoot = rng.uniform(*self.SHOOT_INTERVAL)
        self.t = 0.0

    def _build_nebulae(self, rng):
        palettes = ((35, 60, 140), (90, 45, 130), (30, 100, 110))
        blobs = []
        for color in palettes:
            size = rng.randint(340, 520)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cx = cy = size // 2
            for step in range(14, 0, -1):
                r = int(size / 2 * step / 14)
                alpha = int(16 * (1.0 - step / 14.0) ** 1.5) + 2
                pygame.draw.circle(surf, (*color, alpha), (cx, cy), r)
            blobs.append({
                "surf": surf,
                "x": rng.uniform(-80, self.width - size + 80),
                "y": rng.uniform(-60, self.height - size + 80),
                "depth": rng.uniform(0.01, 0.03),
            })
        return blobs

    def _spawn_shoot(self):
        rng = random.random
        start_x = rng() * self.width * 0.9 + self.width * 0.05
        start_y = rng() * self.height * 0.5
        angle = math.radians(18 + rng() * 32)
        speed = 900 + rng() * 500
        self.shoot = {
            "x": start_x,
            "y": start_y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "age": 0.0,
        }

    def update(self, dt: float):
        self.t += dt
        self.next_shoot -= dt
        if self.shoot is None:
            if self.next_shoot <= 0:
                self._spawn_shoot()
                self.next_shoot = random.uniform(*self.SHOOT_INTERVAL)
        else:
            s = self.shoot
            s["age"] += dt
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            if s["age"] > self.SHOOT_LIFE or s["x"] > self.width + 60:
                self.shoot = None

    def draw(self, surface, yaw: float = 0.0):
        offset = -yaw * 60.0

        for blob in self.nebulae:
            x = int(blob["x"] + offset * blob["depth"] * 8)
            surface.blit(blob["surf"], (x, int(blob["y"])))

        for layer in self.layers:
            par = layer["parallax"] * offset
            for st in layer["stars"]:
                tw = 0.55 + 0.45 * math.sin(self.t * st["speed"] + st["phase"])
                b = int(st["bright"] * (0.55 + 0.45 * tw))
                x = int(st["x"] + par) % self.width
                y = st["y"]
                if st["size"] > 1 and b > 170:
                    warm = (b, b, min(255, b + 20))
                    pygame.draw.circle(surface, warm, (x, int(y)), st["size"])
                    halo = pygame.Surface((st["size"] * 6, st["size"] * 6),
                                          pygame.SRCALPHA)
                    pygame.draw.circle(halo, (b, b, b, 45),
                                       (st["size"] * 3,) * 2, st["size"] * 3)
                    surface.blit(halo, (x - st["size"] * 3,
                                        int(y) - st["size"] * 3))
                else:
                    pygame.draw.circle(surface, (b, b, b), (x, int(y)),
                                       st["size"])

        if self.shoot is not None:
            s = self.shoot
            fade = max(0.0, 1.0 - s["age"] / self.SHOOT_LIFE)
            tail_x = s["x"] - s["vx"] * 0.14
            tail_y = s["y"] - s["vy"] * 0.14
            head = (int(s["x"]), int(s["y"]))
            tail = (int(tail_x), int(tail_y))
            a = int(230 * fade)
            for k in range(6):
                t0, t1 = k / 6.0, (k + 1) / 6.0
                p0 = (int(tail_x + (s["x"] - tail_x) * t0),
                      int(tail_y + (s["y"] - tail_y) * t0))
                p1 = (int(tail_x + (s["x"] - tail_x) * t1),
                      int(tail_y + (s["y"] - tail_y) * t1))
                shade = int(a * (0.25 + 0.75 * t1))
                pygame.draw.line(surface, (shade, shade, min(255, shade + 30)),
                                 p0, p1, max(1, int(3 * (0.4 + 0.6 * t1))))
            if fade > 0.15:
                d = 14
                glow = pygame.Surface((d, d), pygame.SRCALPHA)
                pygame.draw.circle(glow, (200, 230, 255, int(160 * fade)),
                                   (d // 2, d // 2), d // 2)
                surface.blit(glow, (head[0] - d // 2, head[1] - d // 2))
                pygame.draw.circle(surface, (255, 255, 255), head, 2)
