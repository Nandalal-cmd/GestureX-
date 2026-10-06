import math
import random

import pygame

from particles import physics


class ParticleEffect:
    name = "PARTICLE"

    def __init__(self, strength: float = 1.0):
        self.strength = strength

    def update(self, particles, gesture_name, palm, dt):
        pass

    def draw_extra(self, surface, palm):
        pass
