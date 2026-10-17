import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()

from rendering.renderer import Renderer


def _renderer():
    return Renderer(320, 180)


def test_heat_vignette_no_draw_when_cool():
    r = _renderer()
    r.surface.fill((0, 0, 0))
    before = pygame.image.tostring(r.surface, "RGB")
    r.draw_heat_vignette(0.1, False)
    after = pygame.image.tostring(r.surface, "RGB")
    assert before == after


def test_heat_vignette_marks_edges_when_hot():
    r = _renderer()
    r.surface.fill((0, 0, 0))
    r.draw_heat_vignette(1.0, True, 0.0)
    assert sum(r.surface.get_at((1, 1))[:3]) > 0


def test_leaderboard_draws_without_error():
    r = _renderer()
    r.draw_leaderboard([100, 80, 60], 1.0, 0)
    r.draw_leaderboard([], 0.5)
    r.draw_leaderboard([50], 0.0)
