from random import Random

import pytest

from app.config import AppConfig
from effects.fire_effect import COLOR_LIFETIME, FireEffect, flame_color
from gestures.gesture_types import GestureResult, GestureType
from interaction.interaction_engine import InteractionEngine
from particles.particle_system import ParticleSystem
from tracking.landmarks import HandLandmarks


def make_system(count: int = 200) -> ParticleSystem:
    return ParticleSystem(AppConfig(), count=count, bounds=(0.0, 0.0, 1.0, 1.0), rng=Random(11))


def make_hand(*, extended: bool) -> HandLandmarks:
    from tracking.landmarks import (
        INDEX_MCP, INDEX_PIP, INDEX_TIP, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP,
        PINKY_MCP, PINKY_PIP, PINKY_TIP, RING_MCP, RING_PIP, RING_TIP, WRIST,
    )

    points = [(0.5, 0.5)] * 21
    points[WRIST] = (0.5, 0.7)
    for mcp in (INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP):
        points[mcp] = (0.5, 0.5)
    for tip, pip in ((INDEX_TIP, INDEX_PIP), (MIDDLE_TIP, MIDDLE_PIP), (RING_TIP, RING_PIP), (PINKY_TIP, PINKY_PIP)):
        points[pip] = (0.5, 0.5)
        points[tip] = (0.5, 0.3 if extended else 0.6)
    return HandLandmarks(tuple(points))


def test_flame_color_is_hot_when_fresh_and_cool_when_old() -> None:
    hot = flame_color(1.0)
    cold = flame_color(0.0)
    assert hot[0] > cold[0]
    assert hot[1] > cold[1]
    assert hot[2] > cold[2]


def test_flame_color_is_clamped_and_monotonic() -> None:
    assert flame_color(5.0) == flame_color(1.0)
    assert flame_color(-3.0) == flame_color(0.0)
    reds = [flame_color(ratio)[0] for ratio in (0.0, 0.25, 0.55, 1.0)]
    assert reds == sorted(reds)


def test_fire_emits_nothing_without_a_source() -> None:
    system = make_system()
    effect = FireEffect(AppConfig(), rng=Random(1))
    for _ in range(60):
        effect.update(system, 1.0 / 60.0)
        system.update(1.0 / 60.0)
    assert system.active_count == 0


def test_fire_emits_rising_particles_at_the_source() -> None:
    system = make_system()
    effect = FireEffect(AppConfig(), rng=Random(1))
    effect.set_source((0.5, 0.6))
    for _ in range(30):
        effect.update(system, 1.0 / 60.0)
        system.update(1.0 / 60.0)
    assert system.active_count > 0
    near_source = [p for p in system.particles if p.is_alive and abs(p.x - 0.5) < 0.1 and abs(p.y - 0.6) < 0.1]
    assert near_source
    assert any(particle.vy < 0.0 for particle in near_source)


def test_fire_particles_stay_short_lived_for_a_flickering_look() -> None:
    system = make_system()
    effect = FireEffect(AppConfig(), rng=Random(2))
    effect.set_source((0.5, 0.6))
    effect.update(system, 1.0 / 60.0)
    system.update(1.0 / 60.0)
    assert all(particle.max_life <= COLOR_LIFETIME for particle in system.particles if particle.is_alive)


def test_releasing_the_fist_stops_emission_and_the_flame_dies_out() -> None:
    system = make_system()
    effect = FireEffect(AppConfig(), rng=Random(3))
    effect.set_source((0.5, 0.6))
    for _ in range(30):
        effect.update(system, 1.0 / 60.0)
        system.update(1.0 / 60.0)
    assert system.active_count > 0

    effect.set_source(None)
    for _ in range(120):
        effect.update(system, 1.0 / 60.0)
        system.update(1.0 / 60.0)
    assert system.active_count == 0


def test_engine_lights_fire_only_for_a_fist() -> None:
    engine = InteractionEngine(FireEffect(AppConfig(), rng=Random(4)))
    hand = make_hand(extended=False)

    engine.update(GestureResult(GestureType.FIST, 0.9), hand)
    assert engine.is_engaged
    assert engine.fire.source == pytest.approx(hand.interaction_point)

    engine.update(GestureResult(GestureType.OPEN_PALM, 0.9), hand)
    assert not engine.is_engaged

    engine.update(GestureResult(GestureType.FIST, 0.9), None)
    assert not engine.is_engaged


def test_engine_ignores_swipe_events() -> None:
    engine = InteractionEngine(FireEffect(AppConfig(), rng=Random(5)))
    hand = make_hand(extended=True)
    engine.update(GestureResult(GestureType.SWIPE_RIGHT, 1.0), hand)
    assert not engine.is_engaged