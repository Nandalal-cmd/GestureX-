import time
from collections import deque

from utils.smoothing import smooth_point

SWIPE_THRESHOLD = 0.06
SWIPE_COOLDOWN = 0.5
HISTORY_SIZE = 10


class MotionTracker:
    def __init__(self, smoothing_factor: float = 0.65):
        self.smoothing_factor = smoothing_factor
        self.history = deque(maxlen=HISTORY_SIZE)
        self.smoothed = None
        self.velocity = (0.0, 0.0)
        self._last_swipe_time = -float("inf")

    def update(self, position, now=None):
        now = time.monotonic() if now is None else now
        if self.smoothed is None:
            self.smoothed = position
        else:
            self.smoothed = smooth_point(self.smoothed, position, self.smoothing_factor)
        if self.history:
            prev_t, prev_pos = self.history[-1]
            dt = max(now - prev_t, 1e-6)
            self.velocity = ((self.smoothed[0] - prev_pos[0]) / dt,
                             (self.smoothed[1] - prev_pos[1]) / dt)
        self.history.append((now, self.smoothed))
        return self.detect_swipe(now)

    def detect_swipe(self, now):
        if len(self.history) < 2 or (now - self._last_swipe_time) < SWIPE_COOLDOWN:
            return None
        t0, p0 = self.history[0]
        t1, p1 = self.history[-1]
        if t1 - t0 < 0.05:
            return None
        dx = p1[0] - p0[0]
        dy = p1[1] - p0[1]
        if max(abs(dx), abs(dy)) < SWIPE_THRESHOLD:
            return None
        if abs(dx) > abs(dy):
            direction = "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"
        else:
            direction = "SWIPE_DOWN" if dy > 0 else "SWIPE_UP"
        self._last_swipe_time = now
        self.history.clear()
        return direction

    def reset(self):
        self.history.clear()
        self.smoothed = None
        self.velocity = (0.0, 0.0)
