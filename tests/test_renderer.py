"""Headless smoke tests for the Pygame renderer using the SDL dummy video driver."""

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np  # noqa: E402

from app.config import AppConfig  # noqa: E402
from particles.particle_system import ParticleSystem  # noqa: E402
from rendering.renderer import Renderer  # noqa: E402


def make_frame(width: int = 320, height: int = 240) -> np.ndarray:
    return np.zeros((height, width, 3), dtype=np.uint8)


def make_system(count: int = 40) -> ParticleSystem:
    return ParticleSystem(AppConfig(), count=count, bounds=(0.0, 0.0, 1.0, 1.0))


def test_renderer_opens_and_closes_cleanly() -> None:
    renderer = Renderer(320, 240)
    assert renderer.start()
    assert renderer.is_running
    assert renderer.tick(60) >= 0.0
    renderer.stop()
    assert not renderer.is_running
    renderer.stop()


def test_renderer_draws_a_frame_with_live_particles() -> None:
    renderer = Renderer(320, 240)
    assert renderer.start()
    try:
        system = make_system()
        system.fill()
        system.update(1.0 / 60.0)
        renderer.draw(make_frame(), system, "Gesture: FIST (90%)", 59.4)
    finally:
        renderer.stop()


def test_renderer_draws_an_empty_system_without_error() -> None:
    renderer = Renderer(320, 240)
    assert renderer.start()
    try:
        renderer.draw(make_frame(), make_system(), "Gesture: UNKNOWN (0%)", 60.0)
    finally:
        renderer.stop()


def test_renderer_scales_frames_that_do_not_match_the_window() -> None:
    renderer = Renderer(320, 240)
    assert renderer.start()
    try:
        renderer.draw(make_frame(640, 480), make_system(), "Gesture: FIST", 60.0)
    finally:
        renderer.stop()


def test_renderer_start_failure_is_reported_not_raised(monkeypatch: pytest.MonkeyPatch) -> None:
    import pygame

    def boom(*args, **kwargs):
        raise pygame.error("no display")

    monkeypatch.setattr(pygame.display, "set_mode", boom)
    renderer = Renderer(320, 240)
    assert renderer.start() is False
    assert not renderer.is_running