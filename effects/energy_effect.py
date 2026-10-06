import math

import pygame

from particles import physics


class EnergyEffect:
    name = "ENERGY"

    def __init__(self, strength: float = 1.0):
        self.strength = strength
        self.angle = 0.0

    def update(self, particles, gesture_name, palm, dt):
        self.angle += dt * 3.0
        if palm is None:
            return
        for p in particles.alive_particles():
            physics.attract(p, palm, 500 * self.strength, dt)
            physics.orbit(p, palm, 350 * self.strength, dt)

    def draw_extra(self, surface, palm):
        if palm is None:
            return
        cx, cy = int(palm[0]), int(palm[1])
        for r, alpha in ((40, 120), (70, 80), (100, 50)):
            ring = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring, (80, 160, 255, alpha), (r, r), r, 2)
            surface.blit(ring, (cx - r, cy - r))
