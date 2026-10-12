import pygame


class Shockwaves:
    """Expanding, fading ring pulses on impacts and grabs."""

    def __init__(self):
        self._waves = []

    def spawn(self, x, y, color=(255, 220, 150), growth=260.0, life=0.4, start=6):
        self._waves.append({
            "x": float(x), "y": float(y), "r": float(start),
            "growth": growth, "life": life, "age": 0.0, "color": color,
        })

    def update(self, dt):
        for w in self._waves:
            w["r"] += w["growth"] * dt
            w["age"] += dt
        self._waves = [w for w in self._waves if w["age"] < w["life"]]

    def draw(self, surface):
        for w in self._waves:
            k = 1.0 - w["age"] / w["life"]
            r = int(w["r"])
            d = r * 2 + 4
            stroke = pygame.Surface((d, d), pygame.SRCALPHA)
            pygame.draw.circle(stroke, (*w["color"], int(200 * k)),
                               (d // 2, d // 2), r, max(1, int(3 * k)))
            pygame.draw.circle(stroke, (*w["color"], int(70 * k)),
                               (d // 2, d // 2), r + 6, 2)
            surface.blit(stroke, (int(w["x"]) - d // 2, int(w["y"]) - d // 2))

    def reset(self):
        self._waves = []