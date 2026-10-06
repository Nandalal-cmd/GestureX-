import random


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "size", "life", "max_life", "opacity", "color", "alive")

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.size = 3
        self.life = 0.0
        self.max_life = 1.0
        self.opacity = 255
        self.color = (120, 180, 255)
        self.alive = False

    def spawn(self, x, y, vx=0.0, vy=0.0, size=None, max_life=None, color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size if size is not None else random.randint(2, 5)
        self.max_life = max_life if max_life is not None else random.uniform(2.0, 5.0)
        self.life = self.max_life
        self.opacity = 255
        self.color = color if color is not None else (
            random.randint(80, 160), random.randint(140, 220), 255)
        self.alive = True

    def update(self, dt: float, drag: float = 0.98):
        if not self.alive:
            return
        self.vx *= drag
        self.vy *= drag
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        self.opacity = max(0, int(255 * (self.life / self.max_life)))
        if self.life <= 0:
            self.alive = False
