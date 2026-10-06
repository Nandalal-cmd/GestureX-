import random


def attract(p, target, strength, dt):
    dx = target[0] - p.x
    dy = target[1] - p.y
    dist = max((dx * dx + dy * dy) ** 0.5, 1e-3)
    p.vx += (dx / dist) * strength * dt
    p.vy += (dy / dist) * strength * dt


def repel(p, target, strength, dt):
    dx = p.x - target[0]
    dy = p.y - target[1]
    dist = max((dx * dx + dy * dy) ** 0.5, 1e-3)
    p.vx += (dx / dist) * strength * dt
    p.vy += (dy / dist) * strength * dt


def orbit(p, center, strength, dt):
    dx = p.x - center[0]
    dy = p.y - center[1]
    dist = max((dx * dx + dy * dy) ** 0.5, 1e-3)
    p.vx += (-dy / dist) * strength * dt
    p.vy += (dx / dist) * strength * dt
    attract(p, center, strength * 0.15, dt)


def impulse(p, direction, strength):
    p.vx += direction[0] * strength
    p.vy += direction[1] * strength


def random_spawn_position(width, height):
    return (random.uniform(0, width), random.uniform(0, height))
