"""Simulate a full fire-mode frame loop with a synthetic camera and fake fist."""

from random import Random
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.config import AppConfig
from app.main import run_fire
from effects.fire_effect import FireEffect
from gestures.gesture_types import GestureResult, GestureType
from interaction.interaction_engine import InteractionEngine
from particles.particle_system import ParticleSystem

FIST_LANDMARKS = MagicMock()


def build_fist_landmarks() -> MagicMock:
    """A MediaPipe-shaped result whose fingers are folded, so FIST is detected."""
    points = [(0.5, 0.5)] * 21
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        points[pip] = (0.5, 0.5)
        points[tip] = (0.5, 0.62)
    points[4] = (0.1, 0.5)

    landmark = MagicMock()
    landmark.landmark = [MagicMock(x=x, y=y) for x, y in points]

    handedness = MagicMock()
    handedness.classification = [MagicMock(label="Right")]

    result = MagicMock()
    result.multi_hand_landmarks = [landmark]
    result.multi_handedness = [handedness]
    return result


def test_simulated_fist_produces_a_rising_flame() -> None:
    config = AppConfig()
    system = ParticleSystem(config, bounds=(0.0, 0.0, 1.0, 1.0))
    fire = FireEffect(config, rng=Random(9))
    interaction = InteractionEngine(fire)

    detector_result = build_fist_landmarks()
    frame = np.zeros((240, 320, 3), dtype=np.uint8)

    with patch("cv2.cvtColor", return_value=frame):
        from tracking.landmarks import from_mediapipe

        hand = from_mediapipe(detector_result.multi_hand_landmarks[0], "Right")

    peak = 0
    for _ in range(90):
        result = GestureResult(GestureType.FIST, 0.92)
        interaction.update(result, hand)
        fire.update(system, 1.0 / 60.0)
        system.update(1.0 / 60.0)
        peak = max(peak, system.active_count)

    assert peak > 20, f"expected a visible flame, peak was {peak}"
    ys = [p.y for p in system.particles if p.is_alive]
    assert ys
    assert min(ys) < 0.62, "flame particles should rise above the hand"
    assert min(ys) >= 0.0, "flame particles must stay inside the frame"


def test_flame_does_not_escape_the_top_of_the_frame() -> None:
    config = AppConfig()
    system = ParticleSystem(config, bounds=(0.0, 0.0, 1.0, 1.0))
    fire = FireEffect(config, rng=Random(21))
    fire.set_source((0.5, 0.5))
    for _ in range(600):
        fire.update(system, 1.0 / 60.0)
        system.update(1.0 / 60.0)
    assert all(particle.y >= 0.0 for particle in system.particles)


def test_fire_mode_starts_and_exits_cleanly_on_user_quit() -> None:
    config = AppConfig()
    camera = MagicMock()
    camera.start.return_value = True
    camera.read.return_value = np.zeros((240, 320, 3), dtype=np.uint8)

    tracker = MagicMock()
    tracker.start.return_value = True
    tracker.process.return_value = None

    renderer = MagicMock()
    renderer.tick.return_value = 1.0 / 60.0
    renderer.is_running = True

    def stop_running() -> None:
        renderer.is_running = False

    renderer.draw.side_effect = lambda *args, **kwargs: stop_running()

    with patch("app.main.Camera", return_value=camera), patch("app.main.HandTracker", return_value=tracker), patch(
        "app.main.Renderer", return_value=renderer
    ):
        assert run_fire(config) == 0

    camera.stop.assert_called_once()
    tracker.close.assert_called_once()
    renderer.stop.assert_called_once()


def test_fire_mode_reports_camera_failure_without_crashing() -> None:
    camera = MagicMock()
    camera.start.return_value = False
    with patch("app.main.Camera", return_value=camera):
        assert run_fire(AppConfig()) == 1
    camera.stop.assert_called_once()


def test_fire_mode_releases_everything_on_an_unexpected_error() -> None:
    config = AppConfig()
    camera = MagicMock()
    camera.start.return_value = True
    camera.read.return_value = np.zeros((240, 240, 3), dtype=np.uint8)

    tracker = MagicMock()
    tracker.start.return_value = True
    tracker.process.side_effect = RuntimeError("tracking blew up")

    renderer = MagicMock()
    renderer.tick.return_value = 1.0 / 60.0
    renderer.is_running = True

    with patch("app.main.Camera", return_value=camera), patch("app.main.HandTracker", return_value=tracker), patch(
        "app.main.Renderer", return_value=renderer
    ):
        assert run_fire(config) == 1

    camera.stop.assert_called_once()
    tracker.close.assert_called_once()
    renderer.stop.assert_called_once()