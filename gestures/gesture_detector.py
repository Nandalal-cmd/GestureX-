"""Lightweight geometry-based gesture recognition."""

from __future__ import annotations

from app.config import AppConfig
from gestures.gesture_types import GestureResult, GestureType
from tracking.landmarks import (
    INDEX_PIP, INDEX_TIP, MIDDLE_PIP, MIDDLE_TIP, PINKY_PIP, PINKY_TIP,
    RING_PIP, RING_TIP, THUMB_TIP, HandLandmarks,
)
from utils.geometry import distance


class GestureDetector:
    """Classify pinch, open-palm, and fist states using landmark geometry."""

    def __init__(self, config: AppConfig) -> None:
        self._pinch_threshold = 0.045 + config.gesture_sensitivity * 0.035

    def detect(self, hand: HandLandmarks | None) -> GestureResult:
        if hand is None:
            return GestureResult(GestureType.UNKNOWN, 0.0)

        pinch_distance = distance(hand.points[THUMB_TIP], hand.points[INDEX_TIP])
        if pinch_distance < self._pinch_threshold:
            confidence = min(1.0, 1.0 - pinch_distance / self._pinch_threshold)
            return GestureResult(GestureType.PINCH, confidence)

        extended = sum(
            hand.points[tip][1] < hand.points[pip][1]
            for tip, pip in ((INDEX_TIP, INDEX_PIP), (MIDDLE_TIP, MIDDLE_PIP), (RING_TIP, RING_PIP), (PINKY_TIP, PINKY_PIP))
        )
        if extended >= 4:
            return GestureResult(GestureType.OPEN_PALM, min(1.0, 0.65 + extended * 0.0875))
        if extended <= 1:
            return GestureResult(GestureType.FIST, min(1.0, 0.7 + (4 - extended) * 0.075))
        return GestureResult(GestureType.UNKNOWN, 0.25)
