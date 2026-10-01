"""Data models and landmark calculations independent of MediaPipe."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from utils.geometry import Point, average

WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_TIP = 12
RING_MCP = 13
RING_PIP = 14
RING_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_TIP = 20


@dataclass(frozen=True)
class HandLandmarks:
    """The normalized coordinates for one detected hand."""

    points: tuple[Point, ...]
    handedness: str = "Unknown"
    smoothed_palm: Point | None = None

    def __post_init__(self) -> None:
        if len(self.points) != 21:
            raise ValueError("a MediaPipe hand must contain exactly 21 landmarks")

    @property
    def palm_center(self) -> Point:
        """Average stable palm landmarks as the general interaction point."""
        return average(tuple(self.points[index] for index in (WRIST, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP)))

    @property
    def interaction_point(self) -> Point:
        """Return the smoothed palm point used for movement-based interaction."""
        return self.smoothed_palm or self.palm_center

    @property
    def pinch_point(self) -> Point:
        return average((self.points[THUMB_TIP], self.points[INDEX_TIP]))


def from_mediapipe(landmarks: object, handedness: str) -> HandLandmarks:
    """Convert MediaPipe landmark objects to testable application data."""
    points: Sequence[Point] = tuple((landmark.x, landmark.y) for landmark in landmarks.landmark)
    return HandLandmarks(tuple(points), handedness)
