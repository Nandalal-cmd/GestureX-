"""Smoothed hand-motion tracking and event-based swipe recognition."""

from __future__ import annotations

from collections import deque
from time import monotonic

from gestures.gesture_types import GestureResult, GestureType
from utils.geometry import Point


class MotionTracker:
    """Track palm movement and emit a swipe once per cooldown period."""

    def __init__(self, *, minimum_distance: float = 0.18, maximum_duration: float = 0.45, cooldown: float = 0.5) -> None:
        self.minimum_distance = minimum_distance
        self.maximum_duration = maximum_duration
        self.cooldown = cooldown
        self._history: deque[tuple[float, Point]] = deque()
        self._last_swipe = 0.0

    def update(self, point: Point | None, timestamp: float | None = None) -> GestureResult | None:
        """Add a palm point and return a swipe event when its threshold is crossed."""
        if point is None:
            self._history.clear()
            return None
        now = monotonic() if timestamp is None else timestamp
        self._history.append((now, point))
        while self._history and now - self._history[0][0] > self.maximum_duration:
            self._history.popleft()
        if len(self._history) < 2 or now - self._last_swipe < self.cooldown:
            return None

        _, start = self._history[0]
        dx, dy = point[0] - start[0], point[1] - start[1]
        if max(abs(dx), abs(dy)) < self.minimum_distance:
            return None
        if abs(dx) >= abs(dy):
            gesture = GestureType.SWIPE_RIGHT if dx > 0 else GestureType.SWIPE_LEFT
        else:
            gesture = GestureType.SWIPE_DOWN if dy > 0 else GestureType.SWIPE_UP
        confidence = min(1.0, max(abs(dx), abs(dy)) / (self.minimum_distance * 2))
        self._last_swipe = now
        self._history.clear()
        return GestureResult(gesture, confidence)
