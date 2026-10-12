import os

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
SURF = pygame.Surface((640, 360))

from effects.shockwaves import Shockwaves


def test_spawn_and_expand():
    s = Shockwaves()
    s.spawn(100, 100, growth=100.0, life=1.0, start=5)
    before = s._waves[0]["r"]
    s.update(0.5)
    assert s._waves[0]["r"] > before
    assert len(s._waves) == 1


def test_waves_expire():
    s = Shockwaves()
    s.spawn(100, 100, growth=100.0, life=0.1)
    for _ in range(20):
        s.update(0.05)
    assert s._waves == []


def test_draw_headless():
    s = Shockwaves()
    s.spawn(300, 180)
    s.update(0.1)
    s.draw(SURF)
    s.reset()
    assert s._waves == []