import os

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
SURF = pygame.Surface((640, 360))

from effects.popups import Popups


def test_spawn_rises_and_expires():
    p = Popups()
    p.spawn(100, 100, "+5")
    assert len(p._items) == 1
    y0 = p._items[0]["y"]
    p.update(0.1)
    assert p._items[0]["y"] < y0
    for _ in range(20):
        p.update(0.1)
    assert p._items == []


def test_max_items_capped():
    p = Popups(max_items=3)
    for i in range(10):
        p.spawn(i, i, str(i))
    assert len(p._items) == 3


def test_draw_headless():
    p = Popups()
    p.spawn(300, 180, "+10")
    p.update(0.1)
    p.draw(SURF)
    p.reset()
    assert p._items == []
