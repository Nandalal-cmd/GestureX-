import math

import pygame

from effects.galaxy import COMET_DEFS, FACTS, PLANET_DEFS, Galaxy
from gestures.gesture_types import GestureType


def test_facts_cover_all_planets():
    for defn in PLANET_DEFS:
        assert defn[0] in FACTS


def test_asteroid_belt_and_comets_created():
    g = Galaxy()
    assert len(g.asteroids) == 60
    assert len(g.comets) == len(COMET_DEFS)


def test_orientation_clamped_and_smoothed():
    g = Galaxy()
    g.set_orientation(5.0, -5.0)
    assert g.target_yaw <= 1.1
    assert g.target_tilt >= 0.05
    for _ in range(200):
        g.update(0.016, GestureType.UNKNOWN)
    assert abs(g.yaw - g.target_yaw) < 0.05
    assert abs(g.tilt - g.target_tilt) < 0.05


def test_headless_draw():
    pygame.init()
    surface = pygame.Surface((640, 480))
    g = Galaxy()
    for _ in range(5):
        g.update(0.016, GestureType.UNKNOWN)
        g.draw(surface, (320, 240), 1.0)
    assert any(b.screen is not None for b in g.bodies)


def test_comet_ellipse_radius_positive():
    a, ecc, _, _, _ = COMET_DEFS[0]
    for i in range(50):
        phase = i * math.tau / 50
        r = a * (1.0 - ecc * ecc) / (1.0 + ecc * math.cos(phase))
        assert r > 0
