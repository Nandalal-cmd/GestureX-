"""Small reusable smoothing utilities."""

from utils.geometry import Point


def smooth_point(previous: Point | None, current: Point, factor: float) -> Point:
    """Blend a new point with the previous value; lower factors are more responsive."""
    if not 0.0 <= factor < 1.0:
        raise ValueError("factor must be between 0.0 and 1.0")
    if previous is None:
        return current
    return (
        previous[0] * factor + current[0] * (1.0 - factor),
        previous[1] * factor + current[1] * (1.0 - factor),
    )
