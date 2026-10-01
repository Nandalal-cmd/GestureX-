"""Force, drag, and integration helpers applied to particles each frame."""

from __future__ import annotations

from math import exp

from particles.particle import Particle
from utils.geometry import Point

FADE_WINDOW = 2.0


def apply_attraction(particle: Particle, target: Point, strength: float) -> None:
    """Accelerate the particle toward the target, so force is target - particle."""
    particle.vx += (target[0] - particle.x) * strength
    particle.vy += (target[1] - particle.y) * strength


def apply_repulsion(particle: Particle, target: Point, strength: float) -> None:
    """Accelerate the particle away from the target, so force is particle - target."""
    particle.vx += (particle.x - target[0]) * strength
    particle.vy += (particle.y - target[1]) * strength


def apply_drag(particle: Particle, dt: float) -> None:
    """Decay velocity over time so particles settle instead of drifting forever."""
    factor = exp(-particle.drag * dt)
    particle.vx *= factor
    particle.vy *= factor


def integrate(particle: Particle, dt: float) -> None:
    """Move the particle along its velocity and age it by dt seconds."""
    particle.x += particle.vx * dt
    particle.y += particle.vy * dt
    particle.life -= dt


def fade(particle: Particle) -> None:
    """Derive opacity from remaining lifetime so particles fade out before expiry."""
    particle.opacity = min(1.0, particle.life_ratio * FADE_WINDOW)


def step(particle: Particle, dt: float) -> None:
    """Advance one particle by dt seconds, then refresh its opacity."""
    integrate(particle, dt)
    fade(particle)