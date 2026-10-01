"""Gesture values and recognition result data."""

from dataclasses import dataclass
from enum import Enum


class GestureType(str, Enum):
    UNKNOWN = "UNKNOWN"
    OPEN_PALM = "OPEN_PALM"
    FIST = "FIST"
    PINCH = "PINCH"
    SWIPE_LEFT = "SWIPE_LEFT"
    SWIPE_RIGHT = "SWIPE_RIGHT"
    SWIPE_UP = "SWIPE_UP"
    SWIPE_DOWN = "SWIPE_DOWN"


@dataclass(frozen=True)
class GestureResult:
    gesture: GestureType
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
