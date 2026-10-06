from particles.particle import Particle
from particles.particle_system import ParticleSystem
from particles import physics


class P:
    def __init__(self, x, y, vx=0.0, vy=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy


def test_particle_lifetime():
    p = Particle()
    p.spawn(10, 10, max_life=0.5)
    p.update(0.3)
    assert p.alive
    p.update(0.3)
    assert not p.alive


def test_attract_moves_toward_target():
    p = P(0, 0)
    physics.attract(p, (100, 0), 100, 0.1)
    assert p.vx > 0
    assert abs(p.vy) < 1e-9


def test_repel_moves_away():
    p = P(10, 0)
    physics.repel(p, (0, 0), 100, 0.1)
    assert p.vx > 0


def test_particle_system_target():
    ps = ParticleSystem(max_particles=100, target=30)
    ps.fill_to_target(800, 600)
    assert ps.alive_count == 30
