import math

from utils.geometry import clamp, distance


def test_distance_tuple():
    assert abs(distance((0.0, 0.0), (3.0, 4.0)) - 5.0) < 1e-9


class P:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_distance_objects():
    assert abs(distance(P(0, 0), P(0, 2)) - 2.0) < 1e-9


def test_clamp():
    assert clamp(1.5) == 1.0
    assert clamp(-0.5) == 0.0
    assert clamp(0.4) == 0.4
