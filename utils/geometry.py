import math


def distance(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1]) if isinstance(a, tuple) else math.hypot(a.x - b.x, a.y - b.y)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))
