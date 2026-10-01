"""Geometry helpers using normalized hand-landmark coordinates."""

from __future__ import annotations

from math import hypot
from typing import Sequence

Point = tuple[float, float]


def distance(first: Point, second: Point) -> float:
    """Return the Euclidean distance between two normalized points."""
    return hypot(first[0] - second[0], first[1] - second[1])


def average(points: Sequence[Point]) -> Point:
    """Return the average normalized point, rejecting an empty sequence."""
    if not points:
        raise ValueError("at least one point is required")
    return (
        sum(point[0] for point in points) / len(points),
        sum(point[1] for point in points) / len(points),
    )


def normalized_to_screen(point: Point, width: int, height: int, *, mirror: bool = True) -> tuple[int, int]:
    """Convert a normalized camera point into one centralized screen coordinate."""
    x = 1.0 - point[0] if mirror else point[0]
    return (round(x * width), round(point[1] * height))
