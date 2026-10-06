import math

from particles import physics


class GalaxyEffect:
    name = "GALAXY"

    def __init__(self, strength: float = 1.0):
        self.strength = strength

    def update(self, particles, gesture_name, palm, dt):
        if palm is None:
            return
        from gestures.gesture_types import GestureType
        g = gesture_name
        for p in particles.alive_particles():
            if g == GestureType.FIST:
                physics.attract(p, palm, 1600 * self.strength, dt)
            elif g == GestureType.PINCH:
                physics.attract(p, palm, 900 * self.strength, dt)
            else:
                physics.orbit(p, palm, 300 * self.strength, dt)
                physics.attract(p, palm, 60 * self.strength, dt)

    def draw_extra(self, surface, palm):
        pass
