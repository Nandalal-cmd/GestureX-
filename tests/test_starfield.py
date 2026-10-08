import os

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
SURF = pygame.Surface((640, 360))

from effects.starfield import Starfield


def test_init_and_layers():
    sf = Starfield(640, 360)
    assert len(sf.layers) == 3
    assert sum(len(l["stars"]) for l in sf.layers) == 240
    assert len(sf.nebulae) == 3
    assert sf.shoot is None


def test_update_spawns_shooting_star():
    sf = Starfield(640, 360)
    sf.next_shoot = 0.0
    sf.update(0.1)
    assert sf.shoot is not None
    for _ in range(200):
        sf.update(1 / 60)
    assert sf.shoot is None


def test_draw_headless():
    sf = Starfield(640, 360)
    sf.update(0.5)
    sf.draw(SURF, yaw=0.5)
    sf.draw(SURF, yaw=-0.5)
