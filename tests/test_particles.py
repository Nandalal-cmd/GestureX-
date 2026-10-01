from random import Random

import pytest

from app.config import AppConfig
from particles.particle import Particle
from particles.physics import apply_attraction, apply_drag, apply_repulsion, fade, integrate, step
from particles.particle_system import ParticleSystem


def make_system(**kwargs) -> ParticleSystem:
    kwargs.setdefault("rng", Random(7))
    return ParticleSystem(AppConfig(), **kwargs)


def expire_all(system: ParticleSystem) -> None:
    while system.active_count:
        system.update(0.5)


def test_particle_tracks_lifetime_and_reuses_state() -> None:
    particle = Particle(0.1, 0.2, size=2.0, lifetime=3.0)
    assert particle.is_alive and particle.life_ratio == pytest.approx(1.0)
    particle.spawn(0.5, 0.6, lifetime=1.0)
    assert particle.position == (0.5, 0.6)
    assert particle.life == pytest.approx(1.0)
    assert particle.max_life == pytest.approx(1.0)


def test_particle_rejects_invalid_lifetime() -> None:
    with pytest.raises(ValueError, match="lifetime"):
        Particle(0.0, 0.0, lifetime=0.0)


def test_attraction_and_repulsion_move_opposite_ways() -> None:
    particle = Particle(0.0, 0.0)
    apply_attraction(particle, (1.0, 1.0), 0.5)
    assert (particle.vx, particle.vy) == pytest.approx((0.5, 0.5))
    apply_repulsion(particle, (1.0, 1.0), 0.5)
    assert (particle.vx, particle.vy) == pytest.approx((0.0, 0.0))


def test_drag_slows_particles_without_reversing_them() -> None:
    particle = Particle(0.0, 0.0, vx=1.0, vy=-2.0)
    apply_drag(particle, 0.5)
    assert 0.0 < particle.vx < 1.0
    assert -2.0 < particle.vy < 0.0
    apply_drag(particle, 0.5)
    assert particle.vx < 1.0


def test_integrate_moves_by_velocity_and_ages_particle() -> None:
    particle = Particle(0.0, 0.0, vx=2.0, vy=4.0, lifetime=1.0)
    integrate(particle, 0.25)
    assert particle.position == pytest.approx((0.5, 1.0))
    assert particle.life == pytest.approx(0.75)


def test_opacity_fades_out_before_expiry() -> None:
    particle = Particle(0.0, 0.0, lifetime=1.0)
    fade(particle)
    assert particle.opacity == pytest.approx(1.0)
    particle.life = 0.25
    fade(particle)
    assert particle.opacity == pytest.approx(0.5)
    particle.life = 0.0
    fade(particle)
    assert particle.opacity == pytest.approx(0.0)
    assert not particle.is_alive


def test_step_combines_motion_and_fade() -> None:
    particle = Particle(0.0, 0.0, vx=1.0, lifetime=1.0)
    step(particle, 0.5)
    assert particle.position == pytest.approx((0.5, 0.0))
    assert particle.opacity == pytest.approx(1.0)


def test_system_uses_configured_count_and_rejects_invalid_count() -> None:
    config = AppConfig(default_particles=5, max_particles=6)
    assert ParticleSystem(config).capacity == 5
    with pytest.raises(ValueError, match="max_particles"):
        ParticleSystem(config, count=7)


def test_update_reuses_the_pool_without_allocating() -> None:
    system = make_system(count=10, bounds=(0.0, 0.0, 1.0, 1.0))
    before = [id(particle) for particle in system.particles]
    for _ in range(20):
        system.update(1.0 / 60.0)
    assert [id(particle) for particle in system.particles] == before
    assert system.active_count == 10


def test_auto_fill_keeps_the_pool_full_and_otherwise_particles_expire() -> None:
    sustained = make_system(count=6, bounds=(0.0, 0.0, 1.0, 1.0), auto_fill=True)
    for _ in range(200):
        sustained.update(0.5)
        assert sustained.active_count == 6

    fading = make_system(count=6)
    expire_all(fading)
    assert fading.active_count == 0
    fading.update(1.0)
    assert fading.active_count == 0


def test_emit_reuses_expired_particles_and_never_exceeds_capacity() -> None:
    system = make_system(count=4)
    expire_all(system)
    assert system.emit((0.5, 0.5)) == 1
    assert system.active_count == 1
    assert len({id(particle) for particle in system.particles}) == 4

    full = make_system(count=4)
    assert full.emit((0.5, 0.5), count=10) == 4
    assert full.active_count == 4
    assert full.emit((0.5, 0.5), count=10) == 4
    assert full.capacity == 4


def test_emit_overwrites_the_particle_closest_to_expiry_when_full() -> None:
    system = make_system(count=3)
    for index, particle in enumerate(system.particles):
        particle.life = float(index + 1)
        particle.max_life = 10.0
    assert system.emit((0.5, 0.5)) == 1
    assert system.particles[0].life_ratio > 0.0
    assert system.active_count == 3


def test_forces_use_configured_effect_strength_by_default() -> None:
    system = ParticleSystem(AppConfig(effect_strength=0.5), count=1, rng=Random(3))
    particle = system.particles[0]
    particle.x, particle.y, particle.vx, particle.vy = 0.0, 0.0, 0.0, 0.0
    system.attract((1.0, 1.0))
    assert (particle.vx, particle.vy) == pytest.approx((0.5, 0.5))

    system.impulse(1.0, -1.0, strength=2.0)
    assert (particle.vx, particle.vy) == pytest.approx((2.5, -1.5))


def test_repel_pushes_particle_away_from_target() -> None:
    system = make_system(count=1)
    particle = system.particles[0]
    particle.x, particle.y, particle.vx, particle.vy = 1.0, 1.0, 0.0, 0.0
    system.repel((0.0, 0.0), strength=0.25)
    assert (particle.vx, particle.vy) == pytest.approx((0.25, 0.25))