from gestures.gesture_types import GestureType, SWIPES
from particles import physics


class InteractionEngine:
    """Maps gesture state to particle forces."""

    def __init__(self, effect_strength: float = 1.0):
        self.effect_strength = effect_strength
        self.pinch_target = None
        self._swipe_applied = None

    def update(self, particles, gesture, confidence, palm_screen, pinch_screen, dt, width, height):
        strength = self.effect_strength

        if gesture == GestureType.PINCH and pinch_screen is not None:
            self.pinch_target = pinch_screen
            for p in particles.alive_particles():
                physics.attract(p, pinch_screen, 900 * strength, dt)

        elif gesture == GestureType.FIST and palm_screen is not None:
            for p in particles.alive_particles():
                physics.attract(p, palm_screen, 1400 * strength, dt)

        elif gesture == GestureType.OPEN_PALM and palm_screen is not None:
            for p in particles.alive_particles():
                physics.attract(p, palm_screen, 250 * strength, dt)
                physics.orbit(p, palm_screen, 120 * strength, dt)

        elif gesture in SWIPES:
            self.apply_swipe(particles, gesture, strength)

        if gesture != GestureType.PINCH:
            self.pinch_target = None

    def apply_swipe(self, particles, gesture, strength):
        dirs = {
            GestureType.SWIPE_LEFT: (-1.0, 0.0),
            GestureType.SWIPE_RIGHT: (1.0, 0.0),
            GestureType.SWIPE_UP: (0.0, -1.0),
            GestureType.SWIPE_DOWN: (0.0, 1.0),
        }
        d = dirs[gesture]
        for p in particles.alive_particles():
            physics.impulse(p, d, 420 * strength)
