import math

import pygame

from effects.galaxy import BELT_COUNT, COMET_DEFS, FACTS, PLANET_DEFS, Galaxy
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


def test_blast_destroys_asteroids_in_radius():
    g = Galaxy()
    target = g.asteroids[0]
    target["screen"] = (100.0, 100.0)
    target["px"] = 2
    comet = g.comets[0]
    comet["screen"] = (130.0, 100.0)
    comet["px"] = 3
    before = len(g.asteroids), len(g.comets)
    hits = g.blast((104.0, 100.0), radius=6.0)
    assert hits["asteroids"] == [target]
    assert hits["comets"] == []
    assert target not in g.asteroids
    assert (len(g.asteroids), len(g.comets)) == (before[0] - 1, before[1])
    hits2 = g.blast((130.0, 100.0), radius=6.0)
    assert hits2["comets"] == [comet]
    assert comet not in g.comets
    assert g.blast((1000.0, 1000.0)) == {"asteroids": [], "comets": []}


def test_blast_ignores_offscreen_asteroids():
    g = Galaxy()
    assert g.blast((100.0, 100.0), radius=50.0) == \
        {"asteroids": [], "comets": []}


def test_zoom_clamped_and_smoothed():
    g = Galaxy()
    g.set_zoom(9.0)
    assert g.target_zoom <= g.ZOOM_MAX
    g.set_zoom(-1.0)
    assert g.target_zoom >= g.ZOOM_MIN
    g.set_zoom(g.ZOOM_MAX)
    for _ in range(200):
        g.update(0.016, GestureType.UNKNOWN)
    assert abs(g.zoom - g.target_zoom) < 0.05
    g.set_zoom(g.ZOOM_MIN)
    for _ in range(200):
        g.update(0.016, GestureType.UNKNOWN)
    assert abs(g.zoom - g.target_zoom) < 0.05


def test_asteroids_respawn_never_exceed_belt():
    g = Galaxy()
    g.asteroids.clear()
    for _ in range(4000):
        g.update(0.016, GestureType.UNKNOWN)
    assert len(g.asteroids) > 0
    assert len(g.asteroids) <= BELT_COUNT


def test_comets_respawn():
    g = Galaxy()
    g.comets.clear()
    for _ in range(4000):
        g.update(0.016, GestureType.UNKNOWN)
    assert len(g.comets) > 0
    assert len(g.comets) <= len(COMET_DEFS)
    assert all({"a", "ecc", "speed", "phase", "color"} <= set(c)
               for c in g.comets)
